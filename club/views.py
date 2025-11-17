from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from .models import Club
from .forms import ClubForm


@login_required
def club_list(request):
    clubs = Club.objects.all()
    return render(request, "clubs/club_list.html", {"clubs": clubs})


@login_required
def club_detail(request, slug):
    club = get_object_or_404(Club, slug=slug)
    return render(request, "clubs/club_detail.html", {"club": club})


@login_required
def club_create(request):
    if request.method == "POST":
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save(commit=False)
            club.slug = slugify(club.name)
            club.save()
            messages.success(request, "Club wurde erfolgreich erstellt!")
            return redirect("club_detail", slug=club.slug)
    else:
        form = ClubForm()

    return render(request, "clubs/club_form.html", {"form": form, "title": "Club erstellen"})


@login_required
def club_edit(request, slug):
    club = get_object_or_404(Club, slug=slug)

    if request.method == "POST":
        form = ClubForm(request.POST, instance=club)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.slug = slugify(updated.name)
            updated.save()
            messages.success(request, "Club wurde aktualisiert!")
            return redirect("club_detail", slug=updated.slug)

    else:
        form = ClubForm(instance=club)

    return render(request, "clubs/club_form.html", {"form": form, "title": "Club bearbeiten"})
