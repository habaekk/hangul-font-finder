"""Korean font identifier: one cropped text line -> top-k font families with calibrated probabilities.

    pip install torch transformers safetensors pillow numpy huggingface_hub
    python inference.py line.png            # prints top-5
    python inference.py line.png --top 10

From Python:

    from inference import FontIdentifier
    model = FontIdentifier()                # downloads prenny/hangul-font-finder; or pass a local folder
    model.predict(Image.open("line.png"))   # [{"font": ..., "probability": ...}, ...]

The input is ONE line of text, cropped roughly to its box (a little margin is fine).
Text detection is not included: crop lines with any detector, or by hand.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn


class LineFontModel(nn.Module):
    def __init__(self, backbone_config: dict, n_classes: int, embed_dim: int = 512):
        super().__init__()
        import transformers as hf
        data = dict(backbone_config)
        model_type = data.pop("model_type")
        self.backbone = hf.SiglipVisionModel(hf.AutoConfig.for_model(model_type, **data))
        dim = self.backbone.config.hidden_size
        self.embed = nn.Sequential(nn.Linear(dim, embed_dim), nn.LayerNorm(embed_dim))
        self.classifier = nn.Linear(embed_dim, n_classes)

    def forward(self, x):  # x: (N,1,224,224) grey in [-1, 1]
        x = ((x + 1) * 0.5).repeat(1, 3, 1, 1)
        out = self.backbone(pixel_values=(x - 0.5) / 0.5)
        return self.classifier(self.embed(out.pooler_output))


class FontIdentifier:
    def __init__(self, folder: str | Path = "prenny/hangul-font-finder", device: str | None = None):
        """`folder` is a local copy of the model, or a Hugging Face repo id to download."""
        folder = Path(folder)
        if not (folder / "config.json").exists():
            from huggingface_hub import snapshot_download
            folder = Path(snapshot_download(str(folder).replace("\\", "/")))
        self.config = json.loads((folder / "config.json").read_text(encoding="utf-8"))
        self.classes = json.loads((folder / "classes.json").read_text(encoding="utf-8"))
        # Answers are given per group: classes whose Hangul glyphs match (different releases or
        # file formats of one design) are summed, since no image can tell them apart.
        self.groups = json.loads((folder / "groups.json").read_text(encoding="utf-8"))
        self._to_group = np.zeros((len(self.classes), len(self.groups)), np.float32)
        for g in self.groups:
            self._to_group[g["class_ids"], g["id"]] = 1
        self.device = device or ("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
        self.model = LineFontModel(self.config["backbone_config"], len(self.classes), self.config["embed_dim"])
        from safetensors.torch import load_file
        self.model.load_state_dict(load_file(str(folder / "model.safetensors")))
        self.model.to(self.device).eval()
        lay = self.config["layout"]
        self.size, self.rows, self.row_h = lay["size"], lay["rows"], lay["row_h"]
        self.span = self.size * self.rows
        self.temperature = self.config["temperature"]

    # The line is resized to row_h px high (aspect kept) and folded into `rows` rows of a square.
    def _strip(self, image: Image.Image) -> np.ndarray:
        g = image.convert("L")
        w = max(8, round(g.width * self.row_h / g.height))
        return np.asarray(g.resize((w, self.row_h), Image.BICUBIC), np.uint8)

    def _fold(self, strip: np.ndarray, start: int) -> np.ndarray:
        w = strip.shape[1]
        if w < self.span:
            strip = np.concatenate([strip] * (math.ceil((self.span + start) / w) + 1), axis=1)
        piece = strip[:, start:start + self.span]
        if piece.shape[1] < self.span:
            piece = np.concatenate([piece, strip[:, :self.span - piece.shape[1]]], axis=1)
        return piece.reshape(self.row_h, self.rows, self.size).transpose(1, 0, 2).reshape(self.size, self.size)

    def _windows(self, strip: np.ndarray, n: int = 3):
        w = strip.shape[1]
        if w <= self.span:
            return [self._fold(strip, 0)]
        return [self._fold(strip, int(s)) for s in np.linspace(0, w - self.span, n).astype(int)]

    @torch.inference_mode()
    def probabilities(self, images) -> np.ndarray:
        """Calibrated probabilities over font groups (see groups.json), one row per image."""
        p = self.class_probabilities(images) @ self._to_group
        # A few raw classes belong to no group (fonts withdrawn from the answer list);
        # their share is spread over the remaining fonts.
        return p / p.sum(1, keepdims=True)

    @torch.inference_mode()
    def class_probabilities(self, images) -> np.ndarray:
        """Calibrated probabilities over the model's raw classes (classes.json)."""
        stacks = [self._windows(self._strip(im)) for im in images]
        flat = np.stack([w for s in stacks for w in s]).astype(np.float32)[:, None] / 127.5 - 1
        logits = self.model(torch.from_numpy(flat).to(self.device)).float().cpu().numpy()
        out, k = [], 0
        for s in stacks:
            z = logits[k:k + len(s)].mean(0) / self.temperature
            k += len(s)
            z = np.exp(z - z.max())
            out.append(z / z.sum())
        return np.stack(out)

    def predict(self, image: Image.Image, top: int = 5):
        p = self.probabilities([image])[0]
        return [{"font": self.groups[i]["name"], "same_shape_fonts": self.groups[i]["families"],
                 "korean_name": self.groups[i].get("korean_name"), "probability": round(float(p[i]), 4)}
                for i in np.argsort(-p)[:top]]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    here = Path(__file__).resolve().parent
    ap.add_argument("--model", default=str(here) if (here / "config.json").exists() else "prenny/hangul-font-finder",
                    help="local model folder or Hugging Face repo id")
    ap.add_argument("--top", type=int, default=5)
    a = ap.parse_args()
    model = FontIdentifier(a.model)
    for path in a.images:
        print(path)
        for r in model.predict(Image.open(path), a.top):
            print(f"  {r['probability']:.3f}  {r['font']}" + (f" ({r['korean_name']})" if r["korean_name"] else ""))


if __name__ == "__main__":
    main()
