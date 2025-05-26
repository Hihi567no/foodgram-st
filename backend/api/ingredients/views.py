from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Ingredient
from .serializers import IngredientSerializer
from .filters import IngredientFilterSet


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [AllowAny]
    pagination_class = None
    filterset_class = IngredientFilterSet
