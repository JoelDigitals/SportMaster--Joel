# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("player", "Player"),
        ("referee", "Referee"),
        ("timekeeper", "Timekeeper / Secretary"),
        ("coach", "Coach"),
        ("club_admin", "Club Admin"),
        ("federation_admin", "Federation Admin"),
        ("global_admin", "Global Admin"),
    ]

    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="player")
    short_id = models.CharField(max_length=12, unique=True, null=True, blank=True)

    # optional association to club/ federation
    club = models.ForeignKey("club.Club", null=True, blank=True, on_delete=models.SET_NULL)
    federation = models.ForeignKey("federation.Federation", null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.short_id:
            import uuid
            self.short_id = uuid.uuid4().hex[:10]
        super().save(*args, **kwargs)


# -----------------------------
# PLAYER PROFILE (with Player Pass)
# -----------------------------
class PlayerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="player_profile")

    pass_number = models.CharField(max_length=30, unique=True)
    issue_date = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    club = models.ForeignKey("club.Club", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Player Pass {self.pass_number} ({self.user.username})"


# -----------------------------
# REFEREE PROFILE (with Licence)
# -----------------------------
class RefereeProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="referee_profile")

    license_number = models.CharField(max_length=30, unique=True)
    license_level = models.CharField(max_length=50)  # z.B. "DHBL", "Regional", "Basis"
    issue_date = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    federation = models.ForeignKey("federation.Federation", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Referee {self.license_number} ({self.user.username})"


# -----------------------------
# TIMEKEEPER / SECRETARY PROFILE (ZS/ZN)
# -----------------------------
class TimekeeperProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="timekeeper_profile")

    license_number = models.CharField(max_length=30, unique=True)
    qualification = models.CharField(max_length=50)  # z.B. "ZN", "ZS", "ZN/ZS kombiniert"
    issue_date = models.DateField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)

    federation = models.ForeignKey("federation.Federation", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"ZS/ZN {self.license_number} ({self.user.username})"

class Sport(models.Model):
    name = models.CharField(max_length=50, unique=True)  
    slug = models.SlugField(max_length=50, unique=True, blank=True)  # <--- Feld hinzufügen

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
