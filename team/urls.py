from django.urls import path
from . import views

urlpatterns = [
    path("", views.team_list, name="team_list"),
    path("create/", views.team_create, name="team_create"),
    path("<slug:slug>/", views.team_detail, name="team_detail"),
    path("<slug:slug>/public/", views.public_team_view, name="team_public"),
    path("<slug:slug>/members/", views.member_team_view, name="team_detail_members"),
    path("<slug:slug>/members/list/", views.members_list, name="members_list"),
    path("<slug:slug>/trainers/", views.trainer_team_view, name="team_detail_trainer"),

    # lineup
    path("<slug:slug>/lineup/create/", views.lineup_create, name="lineup_create"),
    path("<slug:slug>/lineup/<int:pk>/edit/", views.lineup_edit, name="lineup_edit"),
    path("<slug:slug>/lineup/<int:pk>/delete/", views.lineup_delete, name="lineup_delete"),

    # chat
    path("<slug:slug>/chat/post/", views.chat_post, name="chat_post"),

    # training
    path("<slug:slug>/training/series/create/", views.training_series_create, name="training_series_create"),
    path("<slug:slug>/training/create/", views.training_event_create, name="training_event_create"),
    path("<slug:slug>/training/<int:pk>/delete/", views.training_event_delete, name="training_event_delete"),
    path("<slug:slug>/training/<int:pk>/rsvp/", views.training_rsvp, name="training_rsvp"),

    # penalties
    path("<slug:slug>/penalties/", views.penalties_list, name="penalties_list"),
    path("<slug:slug>/penalties/create/", views.penalty_create, name="penalty_create"),
    path("<slug:slug>/penalties/assign/", views.penalty_assign, name="penalty_assign"),
    path("<slug:slug>/penalties/assign/<int:penalty_id>/<int:user_id>/", views.penalty_assign, name="penalty_assign_quick"),
    path("<slug:slug>/penalties/mark_paid/<int:assigned_id>/", views.penalty_mark_paid, name="penalty_mark_paid"),
    
]
