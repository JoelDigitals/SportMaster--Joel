from django.contrib import admin
from . models import CustomUser, RefereeProfile, PlayerProfile, TimekeeperProfile, Sport

admin.site.register(CustomUser)
admin.site.register(RefereeProfile)
admin.site.register(PlayerProfile)
admin.site.register(TimekeeperProfile)
admin.site.register(Sport)