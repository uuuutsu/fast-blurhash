import importlib.util

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:  # noqa: ARG001
    has_pillow = (importlib.util.find_spec("PIL") is not None) and (importlib.util.find_spec("blurhash") is not None)

    for item in items:
        no_pillow_marker = item.get_closest_marker("no_pillow")

        if has_pillow and no_pillow_marker:
            item.add_marker(pytest.mark.skip(reason="Runs only without Pillow"))
        elif not has_pillow:
            item.add_marker(pytest.mark.skip(reason="Pillow not available"))
