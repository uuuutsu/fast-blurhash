from __future__ import annotations

from typing import TYPE_CHECKING, Final, ParamSpec

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable


P = ParamSpec("P")


def parametrize(**kwargs: object) -> Callable[[Callable[P, None]], Callable[P, None]]:
    def inner(func: Callable[P, None]) -> Callable[P, None]:
        final = func
        for key, value in kwargs.items():
            final = pytest.mark.parametrize(key, value)(final)  # type: ignore[arg-type]
        return final

    return inner


DEFAULT_X_COMPONENTS: Final[int] = 4
DEFAULT_Y_COMPONENTS: Final[int] = 3
