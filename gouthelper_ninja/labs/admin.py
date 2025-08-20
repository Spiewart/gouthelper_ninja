from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import BaselineCreatinine


@admin.register(BaselineCreatinine)
class BaselineCreatinineHistoryAdmin(SimpleHistoryAdmin):
    list_display = (
        "value",
        "patient",
        "created",
        "modified",
        "pk",
    )
    history_list_display = ["status"]
