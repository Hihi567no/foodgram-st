from djoser import views as djoser_views
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .serializers import AvatarSerializer, FoodgramUserWithRecipesSerializer
from recipes.models import Subscription


User = get_user_model()


class FoodgramUserViewSet(djoser_views.UserViewSet):
    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_name="me",
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_name="subscribe",
    )
    def subscribe(self, request, id):
        if self.get_object() == self.request.user:
            return Response({"detail": "Нельзя подписаться на самого себя"}, status=status.HTTP_400_BAD_REQUEST)
        _, created = Subscription.objects.get_or_create(author=self.get_object(), user=self.request.user)
        if not created:
            return Response(
                {
                    "detail": "Пользователь уже подписан на автора",
                    "author": FoodgramUserWithRecipesSerializer(self.get_object(), context={"request": request}).data
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(FoodgramUserWithRecipesSerializer(self.get_object(), context={"request": request}).data, status=status.HTTP_201_CREATED)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="subscriptions",
        url_name="subscriptions",
    )
    def subscriptions(self, request):
        page = self.paginate_queryset(request.user.authors.all())
        data = [
            FoodgramUserWithRecipesSerializer(sub.author, context={"request": request}).data
            for sub in page
        ]
        return self.get_paginated_response(data)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        get_object_or_404(
            Subscription,
            author=self.get_object(),
            user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["put"],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
        url_name="me-avatar",
    )
    def avatar(self, request):
        serializer = self._change_avatar(request.data)
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        data = request.data
        if "avatar" not in data:
            data = {"avatar": None}
        self._change_avatar(data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _change_avatar(self, data):
        instance = self.get_instance()
        serializer = AvatarSerializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer
