from http import HTTPStatus

import pytest
from django.test import RequestFactory
from django.test import TestCase

from gouthelper_ninja.contents.views import Home

pytestmark = pytest.mark.django_db


class TestHome(TestCase):
    def setUp(self):
        self.url = "/"

        # Act
        self.request = RequestFactory().get(self.url)
        self.response = Home.as_view()(self.request)

    def test__view(self):
        # Assert
        assert self.response.status_code == HTTPStatus.OK
