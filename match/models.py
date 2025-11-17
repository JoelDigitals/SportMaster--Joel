from django.db import models
from django.utils import timezone

class Fixture(models.Model):
    home = models.ForeignKey("team.Team", related_name="home_fixtures", on_delete=models.CASCADE)
    away = models.ForeignKey("team.Team", related_name="away_fixtures", on_delete=models.CASCADE)
    venue = models.ForeignKey("venue.Venue", null=True, blank=True, on_delete=models.SET_NULL)
    datetime = models.DateTimeField()
    competition = models.CharField(max_length=255, blank=True)
    round = models.CharField(max_length=50, blank=True)
    referee = models.ForeignKey("accounts.CustomUser", null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_matches")
    status = models.CharField(max_length=30, default="scheduled")  # scheduled, ongoing, finished, canceled
    result_home = models.IntegerField(null=True, blank=True)
    result_away = models.IntegerField(null=True, blank=True)
    # freie Wunschlisten (referee preferences) und Zuweisungen
    referee_preferences = models.ManyToManyField("accounts.CustomUser", related_name="preferred_fixtures", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True)
    short_code = models.CharField(max_length=20, blank=True)
    
    def is_past(self):
        return self.datetime < timezone.now()
    
    def __str__(self):
        return f"{self.home.name} vs {self.away.name} on {self.datetime.strftime('%Y-%m-%d %H:%M')}"