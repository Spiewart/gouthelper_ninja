from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from gouthelper_ninja.genders.models import Gender


@admin.register(Gender)
class GenderAdmin(SimpleHistoryAdmin):
    list_display = (
        "gender",
        "patient",
        "created",
        "pk",
    )
    history_list_display = ["status"]
