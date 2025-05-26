from django.urls import path, include


app_name = "api"


urlpatterns = [
    path("", include("api.users.urls")),
    path("", include("api.ingredients.urls")),
    path("", include("api.recipes.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]