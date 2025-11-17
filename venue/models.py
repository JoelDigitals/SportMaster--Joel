from django.db import models

# Create your models here.
class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    capacity = models.IntegerField(null=True,blank=True)
    contact = models.CharField(max_length=200, blank=True)
    available_slots = models.JSONField(default=list, blank=True)  # optionale Struktur
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name