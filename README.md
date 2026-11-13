# 한글 폰트 파인더 (hangul-font-finder)

**이미지 속 한 줄짜리 한글 글자를 보고, 어떤 무료 한글 폰트인지 알려 줍니다.**

- 무료 한글 폰트 **1,279종**(1,393 패밀리)을 알아봅니다.
- 테두리, 그림자, 입체, 그라데이션, 장평 늘림, 일부 가림, 저화질 압축처럼 꾸민 글자도 맞힙니다.
- OCR도, 글자 한 자씩 자르기도 필요 없습니다. **글자 한 줄을 잘라 낸 이미지 한 장**이면 됩니다.
- 결과마다 **보정된 확률**이 붙습니다. «95% 이상»이라고 하면 실제로 99.6% 맞습니다.
- 합성 이미지만으로 학습했습니다.

🤗 모델: [prenny/hangul-font-finder](https://huggingface.co/prenny/hangul-font-finder)

*English below.*

## 예시

| 입력 | 1위 | 확률 |
|---|---|---:|
| ![](examples/example-1.png) | Black Han Sans | 99.6% |
| ![](examples/example-2.png) | Jua (주아) | 99.6% |
| ![](examples/example-3.png) | Do Hyeon (도현) — 저화질 JPEG | 99.4% |
| ![](examples/example-4.png) | Gaegu (개구) | 99.7% |
| ![](examples/example-5.png) | Song Myung (송명) | 99.7% |
| ![](examples/example-6.png) | Yeon Sung (연성) — 장평 80% | 99.7% |

## 설치와 사용

```bash
git clone https://github.com/habaekk/hangul-font-finder
cd hangul-font-finder
pip install -r requirements.txt

python inference.py examples/example-2.png
#   0.996  Jua (배달의민족 주아)
#   0.000  Hakgyoansim Gongryongal R (학교안심 공룡알 R)
#   ...
```

```python
from PIL import Image
from inference import FontIdentifier

model = FontIdentifier()          # 처음 한 번 허깅페이스에서 가중치(376MB)를 받습니다
model.predict(Image.open("line.png"), top=5)
# [{'font': 'Jua', 'same_shape_fonts': ['BM JUA_TTF', 'Jua'], 'korean_name': ..., 'probability': 0.9955}, ...]
```

- `same_shape_fonts`: 같은 디자인의 다른 판(OTF/TTF, 영문/한글 이름, 구글 폰트판)을 함께 보여 줍니다.
- 입력은 **글자 한 줄**입니다. 여러 줄이 있는 이미지는 줄마다 잘라서 넣어 주세요. 글자 위치를 찾는 기능은 들어 있지 않습니다.
- CUDA, Apple Silicon(MPS), CPU 모두 됩니다.

## 성능

1,279종 중에서 고른 결과입니다. «어려운 합성»은 학습 때 보지 않은 문장·배경·가림 물체로 만든 평가 세트이고, 모든 효과가 섞여 있습니다.

| 평가 세트 | 줄 | top-1 | top-3 | top-5 |
|---|---:|---:|---:|---:|
| 어려운 합성 | 2,702 | **93.3%** | 97.9% | 98.7% |
| 깨끗한 합성 | 1,351 | 97.4% | ≥ 99.2% | ≥ 99.8% |
| 실제 디자인 이미지 (폰트 3종) | 186 | 93.5% | 97.8% | 97.8% |

| 모델이 말한 확률 | 비율 | 실제 정답률 |
|---|---:|---:|
| 95% 이상 | 84% | 99.6% |
| 80 – 95% | 7% | 81% |
| 80% 미만 | 9% | 49% |

쓰는 방법: 95% 이상이면 그대로 믿고, 그보다 낮으면 top-5를 «비슷한 폰트» 후보로 보면 됩니다.

## 한계

- **아는 폰트 안에서만 고릅니다.** 목록에 없는 폰트(유료 폰트 등)를 넣으면 가장 닮은 무료 폰트를 답합니다. 이때는 확률이 낮게 나오는 편입니다.
- 실제 이미지 검증은 폰트 3종, 186줄뿐입니다. 숫자 대부분은 합성 이미지에서 잰 것입니다.
- 굵은 고딕끼리, 같은 회사의 손글씨 폰트끼리 가장 많이 헷갈립니다.
- 한글 위주입니다. 영문·숫자만 있는 줄은 평가하지 않았습니다.
- 폰트 이름만 알려 줍니다. 그 폰트를 어디에 써도 되는지는 각 폰트의 라이선스를 확인해 주세요.

## 라이선스

코드와 가중치는 [MIT](LICENSE)입니다. 가중치는 [SigLIP 2](https://huggingface.co/google/siglip2-base-patch16-224)(Apache-2.0)를 이어서 학습한 것이라 [원 라이선스](LICENSE-SIGLIP2-APACHE-2.0)와 [고지](NOTICE)를 함께 둡니다.

---

## English

**hangul-font-finder** identifies which free Korean font a line of Hangul text is set in.

- Knows **1,279 fonts** (1,393 free Korean font families; releases of one design with matching Hangul are counted once).
- Handles decorated text: outlines, shadows, extrusion, gradients, stretched or condensed text, partial occlusion and low-quality compression.
- No OCR and no per-character segmentation: **one cropped line image** in, top-k fonts out.
- Probabilities are calibrated: lines it rates ≥ 95% are right 99.6% of the time.
- Trained entirely on synthetic images. Weights: [prenny/hangul-font-finder](https://huggingface.co/prenny/hangul-font-finder).

```bash
pip install -r requirements.txt
python inference.py line.png --top 5
```

Accuracy over 1,279 fonts on a held-out hard synthetic set: **top-1 93.3%, top-3 97.9%, top-5 98.7%**. See the model card for details and limitations. Code and weights are MIT-licensed; the weights are fine-tuned from SigLIP 2 (Apache-2.0).
