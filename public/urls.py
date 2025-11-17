# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("sport/<str:sport_name>/", views.sport_overview, name="sports_overview"),
    path("search/", views.search, name="search"),
]
