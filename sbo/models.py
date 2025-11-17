from django.db import models

# Create your models here.
class SBOGame(models.Model):
    fixture = models.OneToOneField("match.Fixture", on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True,blank=True)
    current_score_home = models.IntegerField(default=0)
    current_score_away = models.IntegerField(default=0)
    time_elapsed = models.IntegerField(default=0)  # in seconds
    is_running = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True)
    short_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"SBOGame for Fixture {self.fixture.id}"

class SBOEvent(models.Model):
    game = models.ForeignKey(SBOGame, related_name="events", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50)  # goal, foul, timeout, injury, substitution
    team = models.ForeignKey("team.Team", null=True, blank=True, on_delete=models.SET_NULL)
    player = models.ForeignKey("accounts.CustomUser", null=True, blank=True, on_delete=models.SET_NULL)
    meta = models.JSONField(default=dict, blank=True)  # freies Feld: z.B. time_remaining, penalty_seconds
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True)
    short_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.event_type} at {self.timestamp} in game {self.game.id}"