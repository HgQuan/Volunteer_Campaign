from rest_framework import permissions

class CommentOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, comment):
        return super().has_permission(request, view) and request.user == comment.user

class RatingOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, rating):
        return super().has_permission(request, view) and request.user == rating.user

class CartOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, cart):
        return super().has_permission(request, view) and request.user == cart.user

class CartItemOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, cartitem):
        return super().has_permission(request, view) and request.user == cartitem.cart.user