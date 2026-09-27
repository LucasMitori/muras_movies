from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwner(BasePermission):
    """Object-level check: the request user must be the object's `user`.

    Read access still requires the view's own permission_classes (e.g.
    IsAuthenticatedOrReadOnly) — this class only guards mutation of
    someone else's data once an object has been fetched.
    """

    owner_field = "user"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, self.owner_field, None)
        return owner is not None and owner.pk == request.user.pk
