from django.db import models
from accounts.models import Sport

class Head_Federation(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    country = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(null=True,blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)
    adress = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)

    def get_full_hierarchy(self):
        hierarchy = []
        current = self
        while current:
            hierarchy.append(current)
            current = current.parent
        return hierarchy[::-1]  # Reverse to get top-down order
    
    def __str__(self):
        return self.name

class Federation(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    country = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(null=True,blank=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)
    adress = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    head_federation = models.ForeignKey(Head_Federation, null=True, blank=True, on_delete=models.SET_NULL)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)

    def get_full_hierarchy(self):
        hierarchy = []
        current = self
        while current:
            hierarchy.append(current)
            current = current.parent
        return hierarchy[::-1]  # Reverse to get top-down order
    
    def __str__(self):
        return self.name