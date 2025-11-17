from django.db import models

# Create your models here.
class NewsItem(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField()
    author = models.ForeignKey("accounts.CustomUser", null=True, blank=True, on_delete=models.SET_NULL)
    federation = models.ForeignKey("federation.Federation", null=True, blank=True, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.title