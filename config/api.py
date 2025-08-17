from ninja import NinjaAPI

from gouthelper_ninja.ckddetails.api import router as ckddetails_router
from gouthelper_ninja.dateofbirths.api import router as dateofbirths_router
from gouthelper_ninja.ethnicitys.api import router as ethnicitys_router
from gouthelper_ninja.genders.api import router as genders_router
from gouthelper_ninja.users.api import router as users_router

api = NinjaAPI()

api.add_router("ckddetails", ckddetails_router)
api.add_router("dateofbirths", dateofbirths_router)
api.add_router("ethnicitys", ethnicitys_router)
api.add_router("genders", genders_router)
api.add_router("users", users_router)
