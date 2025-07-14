from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import GoutDetail


@admin.register(GoutDetail)
class GoutDetailHistoryAdmin(SimpleHistoryAdmin):
    list_display = (
        "at_goal",
        "at_goal_long_term",
        "flaring",
        "on_ppx",
        "on_ult",
        "starting_ult",
        "patient",
        "modified",
        "created",
        "pk",
    )
    history_list_display = ["history_of"]
