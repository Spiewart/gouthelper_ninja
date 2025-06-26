from django.urls import resolve
from django.urls import reverse


def test_home():
    assert reverse("contents:home") == "/"
    assert resolve("/").view_name == "contents:home"
