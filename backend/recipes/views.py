from django.shortcuts import redirect, get_object_or_404
from .models import Recipe


def handle_short_link(request, id):
    get_object_or_404(Recipe, id=id)
    return redirect(f'/recipes/{id}')