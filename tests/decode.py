from __future__ import annotations

from re import escape as esc
from typing import TYPE_CHECKING

import pytest
from PIL import Image

from fast_blurhash import DecodeType, PixelMode
from fast_blurhash import decode as fast_blurhash_decode
from fast_blurhash import encode as fast_blurhash_encode
from tests.assets import iterate_images

from .utils import DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS, parametrize

if TYPE_CHECKING:
    from pathlib import Path


@parametrize(
    image_path=iterate_images(),
    height_width=[(30, 40), (30, 400), (300, 40), (300, 400)],
    punch=[1.0, 1.1, 1.2, 3.0],
    decode_type=DecodeType,
    mode=PixelMode,
)
def test_decode(
    image_path: Path,
    height_width: tuple[int, int],
    punch: float,
    decode_type: DecodeType,
    mode: PixelMode,
) -> None:
    with Image.open(image_path) as img:
        blurhash = fast_blurhash_encode(img, DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS)

    _img = fast_blurhash_decode(blurhash, *height_width, punch, as_=decode_type, mode=mode)

    if decode_type == DecodeType.BYTES:
        assert isinstance(_img, bytes)  # type: ignore[unreachable]
        assert len(_img) == height_width[0] * height_width[1] * 3  # type: ignore[unreachable]
    else:
        assert isinstance(_img, Image.Image)
        assert _img.size == height_width
        assert _img.mode == mode


@parametrize(image_path=iterate_images(), components=[("3", 4), (3, "4"), ("3", "4"), (3.0, 4), (3, 4.0), (3.0, 4.0)])
def test_decode_incorrect_type_components(image_path: Path, components: tuple[int, int]) -> None:
    blurhash = fast_blurhash_encode(Image.open(image_path), DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS)
    with pytest.raises(TypeError):
        fast_blurhash_decode(blurhash, *components)


@parametrize(image_path=iterate_images(), height_width=[("3", 4), (3, "4"), ("3", "4")])
def test_decode_incorrect_type_width_height(image_path: Path, height_width: tuple[int | str, int | str]) -> None:
    blurhash = fast_blurhash_encode(Image.open(image_path), DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS)
    with pytest.raises(TypeError):
        fast_blurhash_decode(blurhash, *height_width)  # type: ignore[arg-type]


@parametrize(image_path=iterate_images(), punch=["1", b"123"])
def test_decode_incorrect_type_punch(image_path: Path, punch: float) -> None:
    blurhash = fast_blurhash_encode(Image.open(image_path), DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS)
    with pytest.raises(TypeError):
        fast_blurhash_decode(blurhash, DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS, punch)


@parametrize(image_path=iterate_images(), height_width=[(-1, 4), (3, -1), (-5, -123123), (1 << 64, 1), (1, 1 << 64)])
def test_decode_out_of_bounds_width_height(image_path: Path, height_width: tuple[int, int]) -> None:
    blurhash = fast_blurhash_encode(Image.open(image_path), DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS)
    with pytest.raises(OverflowError):
        fast_blurhash_decode(blurhash, *height_width)


@parametrize(image_path=iterate_images(), punch=[-1000, -1])
def test_decode_out_of_bounds_punch(image_path: Path, punch: float) -> None:
    blurhash = fast_blurhash_encode(Image.open(image_path), DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS)
    with pytest.raises(ValueError, match=esc("punch must be greater than 1")):
        fast_blurhash_decode(blurhash, DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS, punch)
