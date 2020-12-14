from rest_framework import permissions


class PermissionModelMixin:

    def get_permissions(self, *args, **kwargs):
        try:
            # return permission_classes depending on action
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]


class CanManageReminder(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user == view.get_object().creator


class CanAccessReminder(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user == view.get_object().creator or request.user in view.get_object().participants.all()
