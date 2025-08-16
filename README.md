### fast-blurhash

Minimal, fast BlurHash encoder/decoder for Python. A wrapper around the Rust [`fast-blurhash`](https://github.com/Sofiman/fast-blurhash) crate, with fully typed API and support for CPython 3.10–3.13.

### Install

```bash
uv add "fast-blurhash"
# If you want to use PIL functionality
uv add "fast-blurhash[pillow]"
```

### Usage

- **Encode from PIL.Image**
```python
from fast_blurhash import encode
from PIL import Image

with Image.open("image.png") as img:
    h = encode(img, x_components=4, y_components=3)
    print(h)  # e.g. "LEHV6nWB2yk8pyo0adR*.7kCMdnj"
```

- **Encode from raw bytes** (RGB or RGBA)
```python
from fast_blurhash import encode, PixelMode

# pixels: bytes of length width * height * channels
# e.g. Image.tobytes()
blurhash_str = encode(pixels, 4, 3, width=640, height=480, mode=PixelMode.RGB)
```

- **Decode to raw bytes (RGB)**
```python
from fast_blurhash import decode

pixels = decode("LEHV6nWB2yk8pyo0adR*.7kCMdnj", width=32, height=32)
# len(pixels) == 32 * 32 * 3
```

- **Decode to PIL.Image** (requires Pillow)
```python
from fast_blurhash import decode, DecodeType, PixelMode

img = decode("LEHV6nWB2yk8pyo0adR*.7kCMdnj", 32, 32, as_=DecodeType.PIL, mode=PixelMode.RGBA)
img.save("preview.png")
```
