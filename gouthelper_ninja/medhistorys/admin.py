from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import MedHistory


@admin.register(MedHistory)
class MedHistoryHistoryAdmin(SimpleHistoryAdmin):
    list_display = (
        "medhistorytype",
        "history_of",
        "patient",
        "modified",
        "created",
        "pk",
    )
    history_list_display = ["history_of"]
