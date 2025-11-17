from django.contrib import admin
from .models import AgeGroup, Team, Penalty, AssignedPenalty, Team_Game_Plan_H4A, Team_Tabel_H4A, TrainingRSVP, Lineup


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "club", "age_group", "sport", "slug")
    list_filter = ("club", "age_group", "sport")
    search_fields = ("name", "club__name", "slug")

    filter_horizontal = ("players", "trainers")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ("title", "team", "amount")

@admin.register(AssignedPenalty)
class AssignedPenaltyAdmin(admin.ModelAdmin):
    list_display = ("user", "penalty", "team", "paid", "assigned_at")

admin.site.register(Team_Tabel_H4A)
admin.site.register(Team_Game_Plan_H4A)
admin.site.register(TrainingRSVP)
admin.site.register(Lineup)