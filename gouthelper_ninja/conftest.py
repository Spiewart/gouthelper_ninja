import pytest
from django.contrib.auth.models import AnonymousUser

from gouthelper_ninja.users.choices import Roles
from gouthelper_ninja.users.models import User
from gouthelper_ninja.users.tests.factories import PatientFactory
from gouthelper_ninja.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def admin(db):
    return UserFactory(role=Roles.ADMIN, is_staff=True)


@pytest.fixture
def provider(db):
    return UserFactory()


@pytest.fixture
def another_provider(db):
    return UserFactory()


@pytest.fixture
def anon(db):
    return AnonymousUser()


@pytest.fixture
def patient(db):
    return PatientFactory()


@pytest.fixture
def patient_with_provider(db, provider):
    """A patient with a provider."""
    return PatientFactory(provider=provider)


@pytest.fixture
def patient_with_creator(db, provider):
    """A patient with a creator."""
    patient = PatientFactory()
    # Manually set the creator, as PatientFactory
    # doesn't have a direct 'creator' argument
    last_history = patient.history.first()
    last_history.history_user = provider
    last_history.save()
    return patient


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
