import pytest

from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


def pytest_addoption(parser):
    """Add a rules command line option to enable or
    disable rules debugging."""

    parser.addoption(
        "--rules",
        action="store",
        default=False,
        help="Enable rules debugging",
    )


@pytest.fixture(autouse=True)
def rules_debug(request, settings):
    """Method to enable rules debugging based on command line option.
    This seems a little hacky based on the forced reloading of logging,
    but it achieves the desired functionality."""
    if request.config.getoption("--rules"):
        settings.LOGGING.update(
            {
                "loggers": {
                    "rules": {
                        "handlers": ["console"],
                        "level": "DEBUG",
                        "propagate": True,
                    },
                },
            },
        )
        # Force Django to reconfigure logging
        import logging.config

        logging.config.dictConfig(settings.LOGGING)
