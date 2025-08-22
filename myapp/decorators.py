from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import redirect
from .models import Users



# -------------------------- Login Decorator ---------------------------
def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request.user, 'is_active', False):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ---------------------------- Role Decorator ----------------------------
def get_logged_in_user(request):
    user_id = request.session.get("frontend_user_id")
    if user_id:
        try:
            return Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return None
    return None


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = get_logged_in_user(request)
            if not getattr(user, 'is_active', False):
                return redirect('login')
            if user.role not in allowed_roles:
                return HttpResponseForbidden("You are not authorized to view this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

