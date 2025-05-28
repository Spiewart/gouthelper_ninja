from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from gouthelper_ninja.ethnicitys.models import Ethnicity


@admin.register(Ethnicity)
class EthnicityAdmin(SimpleHistoryAdmin):
    list_display = (
        "ethnicity",
        "patient",
        "created",
        "pk",
    )
    history_list_display = ["status"]
