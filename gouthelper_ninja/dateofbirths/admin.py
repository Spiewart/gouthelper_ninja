from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from gouthelper_ninja.dateofbirths.models import DateOfBirth


@admin.register(DateOfBirth)
class DateOfBirthAdmin(SimpleHistoryAdmin):
    list_display = (
        "dateofbirth",
        "patient",
        "created",
        "pk",
    )
    history_list_display = ["status"]
