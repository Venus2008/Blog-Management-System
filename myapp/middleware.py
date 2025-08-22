from .models import Users
from django.contrib.auth.models import AnonymousUser

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        user_id = request.session.get('frontend_user_id')
        if user_id:
            try:
                request.user = Users.objects.get(id=user_id)
            except Users.DoesNotExist:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        return self.get_response(request)
    

        