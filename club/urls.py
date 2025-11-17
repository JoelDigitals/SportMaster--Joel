from django.urls import path
from . import views

urlpatterns = [
    path("", views.club_list, name="club_list"),
    path("create/", views.club_create, name="club_create"),
    path("<slug:slug>/", views.club_detail, name="club_detail"),
    path("<slug:slug>/edit/", views.club_edit, name="club_edit"),
]
