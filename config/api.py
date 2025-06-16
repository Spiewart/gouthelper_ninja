from ninja import NinjaAPI

from gouthelper_ninja.users.api.api import router as users_router

api = NinjaAPI()

api.add_router("users", users_router)
