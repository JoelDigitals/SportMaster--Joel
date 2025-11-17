from django.urls import path
from . import views

urlpatterns = [
    # Head Federation
    path("heads/", views.head_list, name="head_list"),
    path("heads/create/", views.head_create, name="head_create"),
    path("heads/<slug:slug>/", views.head_detail, name="head_detail"),
    path("heads/<slug:slug>/edit/", views.head_edit, name="head_edit"),

    # Federation
    path("", views.federation_list, name="federation_list"),
    path("create/", views.federation_create, name="federation_create"),
    path("<slug:slug>/", views.federation_detail, name="federation_detail"),
    path("<slug:slug>/edit/", views.federation_edit, name="federation_edit"),
]
