from django.db import models

class BlacklistToken(models.Model):
    user = models.CharField(max_length=50, blank=True, null=True)
    token = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = 'blacklist_token'