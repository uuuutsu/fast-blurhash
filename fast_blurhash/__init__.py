"""Fast blurhash.

This module is a thin wrapper around the `blurhash` crate.
"""

from __future__ import annotations

from enum import Enum, auto
from types import ModuleType
from typing import TYPE_CHECKING, Final, Literal, cast, overload

from fast_blurhash import _fast_blurhash  # type: ignore[attr-defined]

pillow_defined = False

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
def encode(  # type: ignore[no-any-unimported]
    image: ImageFile,
    x_components: int,
    y_components: int,
) -> str: ...


def encode(  # type: ignore[no-any-unimported]
    image: bytes | ImageFile,
    x_components: int,
    y_components: int,
    width: int | Default = Default.DEFAULT,
    height: int | Default = Default.DEFAULT,
    *,
    mode: PixelMode = PixelMode.RGB,
) -> str:
    """Encode an image to a BlurHash string.

    Args:
        image: Raw pixel bytes (RGB/RGBA) or a ``PIL.Image``.
        x_components: Number of X components in the hash (1-9).
        y_components: Number of Y components in the hash (1-9).
        width: Image width in pixels (required when ``image`` is bytes).
        height: Image height in pixels (required when ``image`` is bytes).
        mode: Pixel layout of ``image`` when bytes; ignored for ``PIL.Image``.

    Returns:
        BlurHash string.

    Raises:
        TypeError: If ``image`` type is unsupported.
        ValueError: If required ``width``/``height`` are missing for bytes, or
            if arguments are invalid.
        OverflowError: If numeric arguments are out of bounds.
    """
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
    as_: Literal[DecodeType.BYTES] = DecodeType.BYTES,
) -> bytes: ...


@overload
def decode(  # type: ignore[no-any-unimported]
    blurhash: str,
    width: int,
    height: int,
    punch: float = 1.0,
    *,
    as_: Literal[DecodeType.PIL] = DecodeType.PIL,
    mode: PixelMode = PixelMode.RGB,
) -> ImageFile: ...


def decode(  # type: ignore[no-any-unimported]
    blurhash: str,
    width: int,
    height: int,
    punch: float = 1.0,
    *,
    as_: DecodeType = DecodeType.BYTES,
    mode: PixelMode = PixelMode.RGB,
) -> bytes | ImageFile:
    """Decode a BlurHash string to image bytes or a ``PIL.Image``.

    Args:
        blurhash: BlurHash string to decode.
        width: Output image width in pixels.
        height: Output image height in pixels.
        punch: Contrast factor (> 1.0 increases contrast).
        as_: Output type selector: ``DecodeType.BYTES`` or ``DecodeType.PIL``.
        mode: Output pixel mode when ``as_`` is ``DecodeType.PIL``.

    Returns:
        If ``as_`` is ``DecodeType.BYTES``, returns raw RGB bytes of length
        ``width * height * 3``. If ``DecodeType.PIL``, returns a ``PIL.Image``.

    Raises:
        RuntimeError: If ``DecodeType.PIL`` is requested but Pillow is missing.
        ValueError: If arguments are invalid (e.g., ``punch`` <= 1).
        TypeError: If argument types are incorrect.
        OverflowError: If numeric arguments are out of bounds.
    """
    res = _fast_blurhash.decode(blurhash, width, height, punch)
    if as_ == DecodeType.BYTES:
        return cast("bytes", res)

    if as_ == DecodeType.PIL:
        if not pillow_defined:
            raise RuntimeError("PIL is not installed")

        return cast("ImageFile", Image.frombytes(PixelMode.RGB, data=res, size=(width, height)).convert(mode))  # type: ignore[no-any-unimported]

    raise ValueError("Invalid decode type.")


__all__ = ("decode", "encode")
