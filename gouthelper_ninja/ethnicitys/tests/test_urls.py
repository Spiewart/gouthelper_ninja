import uuid

import pytest
from django.urls import resolve
from django.urls import reverse

from gouthelper_ninja.ethnicitys.views import EthnicityUpdateView

pytestmark = pytest.mark.django_db


def test_update_url_resolves():
    url = reverse("ethnicitys:update", kwargs={"pk": uuid.uuid4()})
    assert resolve(url).func.view_class is EthnicityUpdateView
