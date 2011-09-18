from django.contrib.auth.models import User

class GooglePlusBackend:
    supports_inactive_user = False
    
    def authenticate(self, googleplus_user=None):
        if googleplus_user is not None:
            return googleplus_user.user
        else:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
