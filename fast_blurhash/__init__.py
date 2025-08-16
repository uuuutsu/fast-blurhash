"""Fast blurhash.

This module is a thin wrapper around the `blurhash` crate.
"""

from __future__ import annotations

from enum import Enum, auto
from types import ModuleType
from typing import TYPE_CHECKING, Final, cast, overload

from fast_blurhash import _fast_blurhash  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from PIL import Image
    from PIL.ImageFile import ImageFile
else:
    try:
        from PIL import Image
        from PIL.ImageFile import ImageFile

        pillow_defined = True
    except ImportError:
        ImageFile = None  # type: ignore[assignment,misc]
        Image = ModuleType("Image")
        pillow_defined = False


RGB_CHANNELS: Final[int] = 3
RGBA_CHANNELS: Final[int] = 4


class PixelMode(str, Enum):
    RGB = "RGB"
    RGBA = "RGBA"


class DecodeType(Enum):
    BYTES = auto()
    PIL = auto()


class Default(Enum):
    DEFAULT = auto()


@overload
def encode(
    image: bytes,
    x_components: int,
    y_components: int,
    width: int,
    height: int,
    *,
    mode: PixelMode = PixelMode.RGB,
) -> str: ...


@overload
def encode(
    image: ImageFile,
    x_components: int,
    y_components: int,
) -> str: ...


def encode(
    image: bytes | ImageFile,
    x_components: int,
    y_components: int,
    width: int | Default = Default.DEFAULT,
    height: int | Default = Default.DEFAULT,
    *,
    mode: PixelMode = PixelMode.RGB,
) -> str:
    """Encode a binary image to a blurhash string."""
    if pillow_defined and isinstance(image, ImageFile):
        pixels = image.convert(PixelMode.RGB).tobytes()
        return cast(
            "str",
            _fast_blurhash.encode(pixels, x_components, y_components, image.width, image.height, RGB_CHANNELS),
        )
    if isinstance(image, bytes):
        if width is Default.DEFAULT:
            raise ValueError("width is required")
        if height is Default.DEFAULT:
            raise ValueError("height is required")
        return _fast_blurhash.encode(  # type: ignore[no-any-return]
            image,
            x_components,
            y_components,
            width,
            height,
            RGB_CHANNELS if mode == PixelMode.RGB else RGBA_CHANNELS,
        )

    raise TypeError("image must be a bytes or ImageFile (PIL)")


@overload
def decode(
    blurhash: str,
    width: int,
    height: int,
    punch: float = 1.0,
    *,
    as_: DecodeType = DecodeType.BYTES,
) -> bytes: ...


@overload
def decode(
    blurhash: str,
    width: int,
    height: int,
    punch: float = 1.0,
    *,
    as_: DecodeType = DecodeType.PIL,
    mode: PixelMode = PixelMode.RGB,
) -> ImageFile: ...


def decode(
    blurhash: str,
    width: int,
    height: int,
    punch: float = 1.0,
    *,
    as_: DecodeType = DecodeType.BYTES,
    mode: PixelMode = PixelMode.RGB,
) -> bytes | ImageFile:
    """Decode a blurhash string to a binary image."""
    res = _fast_blurhash.decode(blurhash, width, height, punch)
    if as_ == DecodeType.BYTES:
        return cast("bytes", res)

    if as_ == DecodeType.PIL:
        if not pillow_defined:
            raise ImportError("PIL is not installed")

        return cast("ImageFile", Image.frombytes(PixelMode.RGB, data=res, size=(width, height)).convert(mode))

    raise ValueError("Invalid decode type.")


__all__ = ("decode", "encode")
