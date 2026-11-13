# 한글 폰트 파인더

이미지에 있는 한글 한 줄을 넣으면 무슨 폰트인지 알려 줍니다.
무료 한글 폰트 1,279종을 알고 있고, 테두리나 그림자가 들어간 글자, 좀 뭉개진 저화질 이미지에서도 꽤 잘 맞힙니다.

모델 파일은 허깅페이스에 있습니다: [prenny/hangul-font-finder](https://huggingface.co/prenny/hangul-font-finder)

| 입력 | 결과 |
|---|---|
| ![](examples/example-1.png) | Black Han Sans (99.6%) |
| ![](examples/example-2.png) | 주아 (99.6%) |
| ![](examples/example-3.png) | 도현 (99.4%) |
| ![](examples/example-4.png) | 개구 (99.7%) |
| ![](examples/example-5.png) | 송명 (99.7%) |
| ![](examples/example-6.png) | 연성 (99.7%) |

## 써 보기

```bash
git clone https://github.com/habaekk/hangul-font-finder
cd hangul-font-finder
pip install -r requirements.txt

python inference.py examples/example-2.png
```

```
examples/example-2.png
  0.996  Jua (배달의민족 주아)
  0.000  Hakgyoansim Gongryongal R (학교안심 공룡알 R)
  0.000  KCC-Ganpan (KCC-간판체)
```

파이썬에서 쓸 때는 이렇게 하면 됩니다. 처음 실행할 때 모델(376MB)을 한 번 받아 옵니다.

```python
from PIL import Image
from inference import FontIdentifier

model = FontIdentifier()
model.predict(Image.open("line.png"), top=5)
```

몇 가지 알아 두면 좋은 것:

- 한 번에 한 줄씩 넣어야 합니다. 이미지에 글자가 여러 줄이면 줄마다 잘라서 넣어 주세요. 글자가 어디 있는지 찾아 주는 기능은 없습니다.
- 같은 폰트인데 이름만 다른 경우(예: 구글 폰트의 Jua와 배민 주아)는 하나로 묶어서 답하고, `same_shape_fonts`에 이름을 다 적어 줍니다.
- GPU가 없어도 돌아갑니다. M4 맥 CPU로 한 장에 0.05초쯤 걸렸습니다.

## 얼마나 맞히나

학습 때 한 번도 안 본 문장과 배경으로 만든 테스트 이미지 2,702장에서 쟀습니다. 테두리, 입체, 가림, 저화질 같은 효과를 마구 섞은 어려운 이미지들입니다.

| | 1위가 정답 | 3위 안에 정답 | 5위 안에 정답 |
|---|---:|---:|---:|
| 효과를 섞은 이미지 | 93.3% | 97.9% | 98.7% |
| 깨끗한 이미지 | 97.4% | 99% 이상 | 99% 이상 |

결과에 붙는 확률도 믿을 만합니다. 모델이 95% 넘게 확신한 경우가 전체의 84%였는데, 그중 99.6%가 맞았습니다. 그래서 95%가 넘으면 그냥 믿고, 그보다 낮으면 5위까지를 «비슷한 폰트» 정도로 보면 됩니다.

## 이런 건 잘 못합니다

- 목록에 없는 폰트(유료 폰트 같은 것)를 넣으면, 모른다고 하지 않고 가장 닮은 무료 폰트를 답합니다. 대신 이럴 때는 확률이 낮게 나오는 편입니다.
- 위 숫자는 모두 합성 이미지에서 잰 것입니다. 실제 이미지에서는 이보다 낮을 수 있습니다.
- 굵은 고딕체끼리, 한 회사에서 나온 비슷한 손글씨 폰트끼리는 자주 헷갈립니다.
- 한글 위주로 만들었습니다. 영어나 숫자만 있는 줄은 시험해 보지 않았습니다.
- 폰트 이름만 알려 줍니다. 그 폰트를 어디에 써도 되는지는 폰트마다 라이선스를 따로 확인해 주세요.

## 라이선스

MIT입니다. 구글의 [SigLIP 2](https://huggingface.co/google/siglip2-base-patch16-224)(Apache-2.0)를 바탕으로 학습해서, 그쪽 라이선스 원문([LICENSE-SIGLIP2-APACHE-2.0](LICENSE-SIGLIP2-APACHE-2.0))과 [NOTICE](NOTICE)도 같이 넣어 두었습니다.

---

### English

Give it an image of one line of Korean text and it tells you which free Korean font it is. It knows 1,279 fonts and copes with outlines, shadows and low-quality images.

```bash
pip install -r requirements.txt
python inference.py line.png
```

On 2,702 synthetic test images with mixed effects, the right font is first 93.3% of the time and in the top five 98.7% of the time. All numbers come from synthetic images. MIT licensed; the weights are fine-tuned from SigLIP 2 (Apache-2.0). Model files: [prenny/hangul-font-finder](https://huggingface.co/prenny/hangul-font-finder).
