from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from gouthelper_ninja.ults.models import CkdDetail


@admin.register(CkdDetail)
class CkdDetailHistoryAdmin(SimpleHistoryAdmin):
    list_display = (
        "patient",
        "stage",
        "dialysis",
        "dialysis_type",
        "dialysis_duration",
        "updated",
        "created",
        "pk",
    )
    history_list_display = ["status"]
