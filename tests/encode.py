from __future__ import annotations

from re import escape as esc
from typing import TYPE_CHECKING

import pytest
from PIL import Image
from blurhash import encode as blurhash_encode

from fast_blurhash import PixelMode
from fast_blurhash import encode as fast_blurhash_encode
from tests.assets import iterate_images

from .utils import DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS, parametrize

if TYPE_CHECKING:
    from pathlib import Path


@parametrize(
    image_path=iterate_images(),
    x_components=[2, 9, 5],
    y_components=[2, 9, 5],
    mode=PixelMode,
    binary=[True, False],
)
def test_encode(image_path: Path, x_components: int, y_components: int, mode: PixelMode, *, binary: bool) -> None:
    with Image.open(image_path) as img:
        fast_blurhash_str = fast_blurhash_encode(
            img.convert(mode).tobytes() if binary else img,
            x_components,
            y_components,
            width=img.width if binary else 0,
            height=img.height if binary else 0,
            mode=mode,
        )
        blurhash_str = blurhash_encode(img, x_components, y_components)

    assert fast_blurhash_str == blurhash_str


def test_encode_incorrect_type_image() -> None:
    with pytest.raises(TypeError, match=esc("image must be a bytes or ImageFile (PIL)")):
        fast_blurhash_encode("1", DEFAULT_X_COMPONENTS, DEFAULT_Y_COMPONENTS)  # type: ignore[call-overload]


@parametrize(
    image_path=iterate_images(),
    components=[("3", 4), (3, "4"), ("3", "4"), (3.0, 4), (3, 4.0), (3.0, 4.0)],
    mode=PixelMode,
    binary=[True, False],
)
def test_encode_incorrect_type_components(
    image_path: Path, components: tuple[int, int], mode: PixelMode, *, binary: bool
) -> None:
    with Image.open(image_path) as img, pytest.raises(TypeError):
        fast_blurhash_encode(
            img.convert(mode).tobytes() if binary else img,
            *components,
            height=img.height if binary else 0,
            width=img.width if binary else 0,
            mode=mode,
        )


@parametrize(
    image_path=iterate_images(),
    components=[(0, 4), (3, 0), (10, 4), (3, 10), (10, 10), (10, 1000)],
    mode=PixelMode,
    binary=[True, False],
)
def test_encode_incorrect_components(
    image_path: Path, components: tuple[int, int], mode: PixelMode, *, binary: bool
) -> None:
    with (
        Image.open(image_path) as img,
        pytest.raises(ValueError, match=esc("x_components and y_components must be in the range [1, 9]")),
    ):
        fast_blurhash_encode(
            img.convert(mode).tobytes() if binary else img,
            *components,
            width=img.width if binary else 0,
            height=img.height if binary else 0,
            mode=mode,
        )


@parametrize(
    image_path=iterate_images(),
    components=[(-1, 4), (3, -1), (-5, -123123), (1 << 64, 1), (1, 1 << 64)],
    mode=PixelMode,
    binary=[True, False],
)
def test_encode_out_of_bounds_components(
    image_path: Path, components: tuple[int, int], mode: PixelMode, *, binary: bool
) -> None:
    with Image.open(image_path) as img, pytest.raises(OverflowError):
        fast_blurhash_encode(
            img.convert(mode).tobytes() if binary else img,
            *components,
            width=img.width if binary else 0,
            height=img.height if binary else 0,
            mode=mode,
        )


@parametrize(
    image_path=iterate_images(),
    height_width=[("3", 4), (3, "4"), ("3", "4")],
    mode=PixelMode,
)
def test_encode_incorrect_type_width_height(
    image_path: Path, height_width: tuple[int | str, int | str], mode: PixelMode
) -> None:
    with Image.open(image_path) as img, pytest.raises(TypeError):
        fast_blurhash_encode(
            img.convert(mode).tobytes(),
            DEFAULT_X_COMPONENTS,
            DEFAULT_Y_COMPONENTS,
            *height_width,  # type: ignore[arg-type]
            mode=mode,
        )


@parametrize(
    image_path=iterate_images(),
    height_width=[(0, 4), (3, 0), (10, 4), (3, 10), (10, 10), (10, 1000)],
    mode=PixelMode,
)
def test_encode_incorrect_width_height(image_path: Path, height_width: tuple[int, int], mode: PixelMode) -> None:
    with (
        Image.open(image_path) as img,
        pytest.raises(
            ValueError,
            match=esc(
                "width and height must be greater than 0"
                if 0 in height_width
                else "pixels length does not match width * height"
            ),
        ),
    ):
        fast_blurhash_encode(
            img.convert(mode).tobytes(),
            DEFAULT_X_COMPONENTS,
            DEFAULT_Y_COMPONENTS,
            *height_width,
            mode=mode,
        )


@parametrize(
    image_path=iterate_images(),
    height_width=[(-1, 4), (3, -1), (-5, -123123), (1 << 64, 1), (1, 1 << 64)],
    mode=PixelMode,
)
def test_encode_out_of_bounds_width_height(image_path: Path, height_width: tuple[int, int], mode: PixelMode) -> None:
    with Image.open(image_path) as img, pytest.raises(OverflowError):
        fast_blurhash_encode(
            img.convert(mode).tobytes(),
            DEFAULT_X_COMPONENTS,
            DEFAULT_Y_COMPONENTS,
            *height_width,
            mode=mode,
        )
