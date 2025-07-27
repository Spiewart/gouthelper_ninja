from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from gouthelper_ninja.ults.models import Ult


@admin.register(Ult)
class UltHistoryAdmin(SimpleHistoryAdmin):
    list_display = (
        "patient",
        "num_flares",
        "freq_flares",
        "indication",
        "modified",
        "created",
        "pk",
    )
    ordering = ("-modified",)
