from django.contrib.auth.models import User

from facebook.models import FacebookUser

class FacebookBackend:
    supports_inactive_user = False
    
    def authenticate(self, fb_user=None):
        if fb_user is not None:
            return fb_user.user
        else:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
