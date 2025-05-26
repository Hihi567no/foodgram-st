from django.urls import path
from . import views


app_name = "recipes"


urlpatterns = [
    path("s/<int:id>/", views.handle_short_link, name="short_link"),
]