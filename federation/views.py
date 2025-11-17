from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify

from .models import Head_Federation, Federation
from .forms import HeadFederationForm, FederationForm


# --------------------------
# HEAD FEDERATION
# --------------------------

@login_required
def head_list(request):
    heads = Head_Federation.objects.all()
    return render(request, "federation/head_list.html", {"heads": heads})


@login_required
def head_detail(request, slug):
    head = get_object_or_404(Head_Federation, slug=slug)
    return render(request, "federation/head_detail.html", {"head": head})


@login_required
def head_create(request):
    if request.method == "POST":
        form = HeadFederationForm(request.POST)
        if form.is_valid():
            hf = form.save(commit=False)
            hf.slug = slugify(hf.name)
            hf.save()
            messages.success(request, "Dachverband erfolgreich erstellt!")
            return redirect("head_detail", slug=hf.slug)
    else:
        form = HeadFederationForm()

    return render(request, "federation/head_form.html", {"form": form, "title": "Dachverband erstellen"})


@login_required
def head_edit(request, slug):
    head = get_object_or_404(Head_Federation, slug=slug)

    if request.method == "POST":
        form = HeadFederationForm(request.POST, instance=head)
        if form.is_valid():
            hf = form.save(commit=False)
            hf.slug = slugify(hf.name)
            hf.save()
            messages.success(request, "Dachverband wurde aktualisiert!")
            return redirect("head_detail", slug=hf.slug)
    else:
        form = HeadFederationForm(instance=head)

    return render(request, "federation/head_form.html", {"form": form, "title": "Dachverband bearbeiten"})


# --------------------------
# FEDERATION
# --------------------------

@login_required
def federation_list(request):
    federations = Federation.objects.all()
    return render(request, "federation/federation_list.html", {"federations": federations})


@login_required
def federation_detail(request, slug):
    federation = get_object_or_404(Federation, slug=slug)
    return render(request, "federation/federation_detail.html", {"federation": federation})


@login_required
def federation_create(request):
    if request.method == "POST":
        form = FederationForm(request.POST)
        if form.is_valid():
            fed = form.save(commit=False)
            fed.slug = slugify(fed.name)
            fed.save()
            messages.success(request, "Verband erfolgreich erstellt!")
            return redirect("federation_detail", slug=fed.slug)
    else:
        form = FederationForm()

    return render(request, "federation/federation_form.html", {"form": form, "title": "Verband erstellen"})


@login_required
def federation_edit(request, slug):
    federation = get_object_or_404(Federation, slug=slug)

    if request.method == "POST":
        form = FederationForm(request.POST, instance=federation)
        if form.is_valid():
            fed = form.save(commit=False)
            fed.slug = slugify(fed.name)
            fed.save()
            messages.success(request, "Verband aktualisiert!")
            return redirect("federation_detail", slug=fed.slug)
    else:
        form = FederationForm(instance=federation)

    return render(request, "federation/federation_form.html", {"form": form, "title": "Verband bearbeiten"})
