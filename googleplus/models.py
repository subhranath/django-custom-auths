from django.contrib.auth.models import User
from django.db import models

class GooglePlusUser(models.Model):
    """Stores Google+ user specific details. 
    """
    user = models.OneToOneField(User)
    access_token = models.TextField(db_index=True)
    expiry_at = models.DateTimeField(null=True)
    googleplus_id = models.CharField(max_length=100, unique=True, db_index=True)
    googleplus_display_name = models.CharField(max_length=100, unique=True, db_index=True)
    
    def __unicode__(self):
        return unicode(self.id) + u' | ' + unicode(self.googleplus_id)
    