# teams/models.py (additions)
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, date
from django.core.exceptions import ValidationError
from club.models import Sport

User = settings.AUTH_USER_MODEL

class Lineup(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="lineups")
    name = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="lineups")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_lineups")
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} - {self.name or 'Aufstellung'}"

class TrainingSeries(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="training_series")
    # weekday: 0=Mon ... 6=Sun
    weekday = models.PositiveSmallIntegerField(choices=[(i, d) for i,d in enumerate(['Mo','Di','Mi','Do','Fr','Sa','So'])])
    time = models.TimeField()
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} Serie {self.get_weekday_display()} {self.time}"

    def generate_events(self):
        """
        erzeugt TrainingEvent-Einträge von start_date bis end_date jeweils am angegebenen Wochentag
        returns number created
        """
        from datetime import timedelta
        created = 0
        current = self.start_date
        # move to first matching weekday
        days_ahead = (self.weekday - current.weekday()) % 7
        current = current + timedelta(days=days_ahead)
        while current <= self.end_date:
            start_dt = timezone.make_aware(timezone.datetime.combine(current, self.time))
            # avoid duplicates
            if not TrainingEvent.objects.filter(team=self.team, start=start_dt).exists():
                TrainingEvent.objects.create(team=self.team, start=start_dt, created_by=self.created_by, series=self)
                created += 1
            current = current + timedelta(days=7)
        return created

class TrainingEvent(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="training_events")
    start = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    series = models.ForeignKey(TrainingSeries, null=True, blank=True, on_delete=models.SET_NULL, related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team.name} Training {self.start}"

class TrainingRSVP(models.Model):
    STATUS_CHOICES = (("yes","Yes"),("no","No"),("maybe","Maybe"))
    training = models.ForeignKey(TrainingEvent, on_delete=models.CASCADE, related_name="rsvps")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    comment = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("training", "user")

class Message(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class AgeGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    order = models.PositiveIntegerField(default=0, help_text="Sorting index")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order"]

class Team(models.Model):
    name = models.CharField(max_length=255)
    club = models.ForeignKey("club.Club", on_delete=models.CASCADE)
    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)

    players = models.ManyToManyField("accounts.CustomUser", related_name="teams", blank=True)
    trainers = models.ManyToManyField("accounts.CustomUser", related_name="coached_teams", blank=True)
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='cashier_for_teams')

    short_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.club.name})"

    def clean(self):
        """Players dürfen nur User mit Rolle 'player' UND gültigem PlayerPass sein."""
        if self.pk:  # nur prüfen, wenn Team schon gespeichert ist
            for p in self.players.all():
                if p.role != "player":
                    raise ValidationError(f"{p.username} ist kein Spieler.")
                if not hasattr(p, "player_profile"):
                    raise ValidationError(f"{p.username} hat keinen gültigen Spielerpass.")


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.full_clean()

class Penalty(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="penalty_catalog")
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.amount} €)"

class AssignedPenalty(models.Model):
    team = models.ForeignKey("Team", on_delete=models.CASCADE, related_name="assigned_penalties")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    penalty = models.ForeignKey(Penalty, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    paid = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="penalties_assigned")

    def __str__(self):
        return f"{self.user} - {self.penalty.title} - {'paid' if self.paid else 'open'}"

class Team_Tabel_H4A(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    eingebetteter_code = models.TextField(null=True, blank=True)  # Feld für eingebetteten Code

class Team_Game_Plan_H4A(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    eingebetteter_code = models.TextField(null=True, blank=True)  # Feld für eingebetteten Code

    
