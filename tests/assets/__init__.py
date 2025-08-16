from collections.abc import Iterable
from pathlib import Path

IMG_EXT = (".jpg", ".png")


def iterate_images() -> Iterable[Path]:
    """Iterate over all images in the assets directory."""
    for file in Path(__file__).parent.iterdir():
        if file.is_file() and file.suffix in IMG_EXT:
            yield file
