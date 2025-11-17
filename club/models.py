from django.db import models
from accounts.models import Sport

class Club(models.Model):
    name = models.CharField(max_length=255)
    federation = models.ForeignKey("federation.Federation", null=True, blank=True, on_delete=models.SET_NULL)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(null=True,blank=True)
    phone = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.name