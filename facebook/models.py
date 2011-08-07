from django.contrib.auth.models import User
from django.db import models

class FacebookUser(models.Model):
    """Stores facebook user specific details. 
    """
    user = models.OneToOneField(User)
    access_token = models.TextField(db_index=True)
    expiry_at = models.DateTimeField(null=True)
    fb_id = models.CharField(max_length=100, unique=True, db_index=True)
    fb_username = models.CharField(max_length=100, unique=True, db_index=True)
    
    def __unicode__(self):
        return unicode(self.id) + u' | ' + unicode(self.fb_id)
    