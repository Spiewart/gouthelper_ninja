from ninja import NinjaAPI

api = NinjaAPI()

api.add_router("/users/", "gouthelper_ninja.users.api.router")
