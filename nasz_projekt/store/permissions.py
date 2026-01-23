import copy
from rest_framework import permissions


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class CanViewBag(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_bag')


class CanViewCart(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_cart')


class CanViewOrder(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_order')
