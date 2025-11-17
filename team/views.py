# teams/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from accounts.models import Sport, CustomUser
from .models import Team, Lineup, TrainingSeries, TrainingEvent, TrainingRSVP, Message, AgeGroup, Penalty, AssignedPenalty, Team_Game_Plan_H4A, Team_Tabel_H4A
from .forms import TeamForm, LineupForm, TrainingSeriesForm, TrainingEventForm, MessageForm, PenaltyForm


# ------------------------------------------------------------------
# Helper permission checks
# ------------------------------------------------------------------
def is_trainer(user, team):
    if not user.is_authenticated:
        return False
    return team.trainers.filter(pk=user.pk).exists() or user.role in ("club_admin", "global_admin", "federation_admin")

def is_player(user, team):
    if not user.is_authenticated:
        return False
    return team.players.filter(pk=user.pk).exists()

def is_cashier(user, team):
    """Kassenwart (cashier) kann Strafen erstellen/zuweisen/bezahlen."""
    if not user.is_authenticated:
        return False
    # team.cashier should be a FK to user on Team model
    return getattr(team, "cashier", None) and team.cashier_id == user.id

# ------------------------------------------------------------------
# Team list / detail / create / edit (unchanged except contexts)
# ------------------------------------------------------------------
@login_required
def team_list(request):
    teams = Team.objects.select_related("club", "age_group").all()
    return render(request, "teams/team_list.html", {"teams": teams})

@login_required
def team_detail(request, slug):
    team = get_object_or_404(Team, slug=slug)
    return render(request, "teams/team_detail.html", {"team": team})

@login_required
def team_create(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.slug = slugify(team.name)
            team.save()
            form.save_m2m()
            messages.success(request, "Team erfolgreich erstellt!")
            return redirect("team_detail", slug=team.slug)
    else:
        form = TeamForm()

    return render(request, "teams/team_form.html", {"form": form, "title": "Team erstellen"})

@login_required
def team_edit(request, slug):
    team = get_object_or_404(Team, slug=slug)

    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            t = form.save(commit=False)
            t.slug = slugify(t.name)
            t.save()
            form.save_m2m()
            messages.success(request, "Team aktualisiert!")
            return redirect("team_detail", slug=t.slug)
    else:
        form = TeamForm(instance=team)

    return render(request, "teams/team_form.html", {"form": form, "title": "Team bearbeiten"})

# ------------------------------------------------------------------
# Public team view
# ------------------------------------------------------------------
def public_team_view(request, slug):
    team = get_object_or_404(Team, slug=slug)
    now = timezone.now()

    upcoming_matches = getattr(team, "upcoming_matches", [])[:6]

    public_lineups = Lineup.objects.filter(
        team=team, is_public=True, date__gte=now
    ).order_by("date")[:6]

    # Game plan embed (H4A Spielplan)
    gameplan_obj = Team_Game_Plan_H4A.objects.filter(team=team).first()
    gameplan_html = gameplan_obj.eingebetteter_code if gameplan_obj else ""

    # Table embed (H4A Tabelle)
    table_obj = Team_Tabel_H4A.objects.filter(team=team).first()
    table_html = table_obj.eingebetteter_code if table_obj else ""

    penalties = Penalty.objects.filter(team=team) if hasattr(Penalty, "__name__") else []

    context = {
        "team": team,
        "upcoming_matches": upcoming_matches,
        "public_lineups": public_lineups,
        "gameplan_html": gameplan_html,
        "table_html": table_html,
        "penalties": penalties,
        "now": now,
    }
    return render(request, "teams/public_team.html", context)


# ------------------------------------------------------------------
# Member view (players)
# ------------------------------------------------------------------
@login_required
def member_team_view(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not (is_player(request.user, team) or is_trainer(request.user, team)):
        return HttpResponseForbidden("Du bist kein Mitglied dieses Teams.")

    now = timezone.now()
    # only upcoming lineups (for upcoming games)
    lineups = Lineup.objects.filter(team=team, date__gte=now).order_by("date")

    # trainings: next events only (we will slice to 6 in template, but fetch ordered)
    trainings = TrainingEvent.objects.filter(team=team, start__gte=now).order_by("start")

    # Chat messages (latest first) - paginate
    messages_qs = Message.objects.filter(team=team).order_by("-created_at")
    paginator = Paginator(messages_qs, 30)
    page = request.GET.get("page", 1)
    messages_page = paginator.get_page(page)

    # RSVP mapping for quick access: training.id -> RSVP instance
    rsvps = {}
    # prefetch rsvps for the user in one go
    user_rsvps = TrainingRSVP.objects.filter(training__in=trainings, user=request.user)
    for r in user_rsvps:
        rsvps[r.training_id] = r

    # penalties and assigned penalties for members view (show who owes/paid)
    penalties = Penalty.objects.filter(team=team).order_by("title") if hasattr(Penalty, '__name__') else []
    assigned_penalties = AssignedPenalty.objects.filter(team=team).select_related("user", "penalty").order_by("-assigned_at") if hasattr(AssignedPenalty, '__name__') else []

    context = {
        "team": team,
        "lineups": lineups,
        "trainings": trainings,
        "messages": messages_page,
        "rsvps": rsvps,
        "penalties": penalties,
        "assigned_penalties": assigned_penalties,
        "now": now,
    }
    return render(request, "teams/member_team.html", context)

# ------------------------------------------------------------------
# Trainer view
# ------------------------------------------------------------------
@login_required
def trainer_team_view(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not is_trainer(request.user, team):
        return HttpResponseForbidden("Nur Trainer dürfen hierhin.")

    now = timezone.now()
    # lineups (upcoming + recent)
    lineups = Lineup.objects.filter(team=team).order_by("-date")

    # trainings (show all future trainings - template may slice)
    trainings = TrainingEvent.objects.filter(team=team).order_by("start")

    series = TrainingSeries.objects.filter(team=team).order_by("-created_at")

    penalties = Penalty.objects.filter(team=team).order_by("title") if hasattr(Penalty, '__name__') else []
    assigned_penalties = AssignedPenalty.objects.filter(team=team).select_related("user", "penalty").order_by("-assigned_at") if hasattr(AssignedPenalty, '__name__') else []

    context = {
        "team": team,
        "lineups": lineups,
        "trainings": trainings,
        "series": series,
        "penalties": penalties,
        "assigned_penalties": assigned_penalties,
        "now": now,
    }
    return render(request, "teams/trainer_team.html", context)

# ------------------------------------------------------------------
# LINEUP CRUD (Trainer-only)
# ------------------------------------------------------------------
@login_required
def lineup_create(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not is_trainer(request.user, team):
        return HttpResponseForbidden("Nur Trainer können Aufstellungen erstellen.")

    if request.method == "POST":
        form = LineupForm(request.POST)
        if form.is_valid():
            lineup = form.save(commit=False)
            lineup.team = team
            lineup.created_by = request.user
            lineup.save()
            form.save_m2m()
            messages.success(request, "Aufstellung gespeichert.")
            return redirect("team_detail_members", slug=team.slug)
    else:
        form = LineupForm()
        form.fields["players"].queryset = team.players.all()

    return render(request, "teams/lineup_form.html", {"form": form, "team": team, "title": "Aufstellung erstellen"})

@login_required
def lineup_edit(request, slug, pk):
    team = get_object_or_404(Team, slug=slug)
    lineup = get_object_or_404(Lineup, pk=pk, team=team)
    if not is_trainer(request.user, team):
        return HttpResponseForbidden("Nur Trainer können Aufstellungen bearbeiten.")

    if request.method == "POST":
        form = LineupForm(request.POST, instance=lineup)
        if form.is_valid():
            form.save()
            messages.success(request, "Aufstellung aktualisiert.")
            return redirect("team_detail_members", slug=team.slug)
    else:
        form = LineupForm(instance=lineup)
        form.fields["players"].queryset = team.players.all()

    return render(request, "teams/lineup_form.html", {"form": form, "team": team, "title": "Aufstellung bearbeiten"})

@login_required
def lineup_delete(request, slug, pk):
    team = get_object_or_404(Team, slug=slug)
    lineup = get_object_or_404(Lineup, pk=pk, team=team)
    if not is_trainer(request.user, team):
        return HttpResponseForbidden("Nur Trainer können Aufstellungen löschen.")

    if request.method == "POST":
        lineup.delete()
        messages.success(request, "Aufstellung gelöscht.")
        return redirect("team_detail_members", slug=team.slug)

    return render(request, "teams/confirm_delete.html", {"object": lineup, "team": team, "title": "Aufstellung löschen"})

# ------------------------------------------------------------------
# Chat (simple DB chat)
# ------------------------------------------------------------------
@login_required
def chat_post(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not (is_player(request.user, team) or is_trainer(request.user, team)):
        return HttpResponseForbidden("Nur Teammitglieder dürfen chatten.")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.team = team
            msg.user = request.user
            msg.save()
            messages.success(request, "Nachricht gesendet.")
            return redirect(request.META.get("HTTP_REFERER", reverse("team_detail_members", kwargs={"slug": slug})))
    return redirect("team_detail_members", slug=slug)

# ------------------------------------------------------------------
# Trainings: series + events
# ------------------------------------------------------------------
@login_required
def training_series_create(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not is_trainer(request.user, team):
        return HttpResponseForbidden("Nur Trainer können Trainingsserien erstellen.")

    if request.method == "POST":
        form = TrainingSeriesForm(request.POST)
        if form.is_valid():
            series = form.save(commit=False)
            series.team = team
            series.created_by = request.user
            series.save()
            created_count = series.generate_events()
            messages.success(request, f"Trainingsserie erstellt ({created_count} Termine angelegt).")
            return redirect("team_detail_trainer", slug=team.slug)
    else:
        form = TrainingSeriesForm()
    return render(request, "teams/training_series_form.html", {"form": form, "team": team, "title": "Trainingsserie erstellen"})

@login_required
def training_event_create(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not is_trainer(request.user, team):
        return HttpResponseForbidden("Nur Trainer können Trainings erstellen.")

    if request.method == "POST":
        form = TrainingEventForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.team = team
            ev.created_by = request.user
            ev.save()
            messages.success(request, "Training erstellt.")
            return redirect("team_detail_trainer", slug=team.slug)
    else:
        form = TrainingEventForm()
    return render(request, "teams/training_event_form.html", {"form": form, "team": team, "title": "Training erstellen"})

@login_required
def training_event_delete(request, slug, pk):
    team = get_object_or_404(Team, slug=slug)
    ev = get_object_or_404(TrainingEvent, pk=pk, team=team)
    if not is_trainer(request.user, team):
        return HttpResponseForbidden("Nur Trainer können Trainings löschen.")

    if request.method == "POST":
        ev.delete()
        messages.success(request, "Training gelöscht.")
        return redirect("team_detail_trainer", slug=team.slug)
    return render(request, "teams/confirm_delete.html", {"object": ev, "team": team, "title": "Training löschen"})

# ------------------------------------------------------------------
# RSVP (now accepts optional comment when declining)
# ------------------------------------------------------------------
@login_required
def training_rsvp(request, slug, pk):
    team = get_object_or_404(Team, slug=slug)
    ev = get_object_or_404(TrainingEvent, pk=pk, team=team)

    if not (is_player(request.user, team) or is_trainer(request.user, team)):
        return HttpResponseForbidden("Nur Teammitglieder können zusagen/absagen.")

    if request.method == "POST":
        status = request.POST.get("status")
        if status not in ("yes", "no", "maybe"):
            messages.error(request, "Ungültiger Status.")
            return redirect(request.META.get("HTTP_REFERER", reverse("team_detail_members", kwargs={"slug": slug})))

        comment = request.POST.get("comment", "").strip() or None
        rsvp, created = TrainingRSVP.objects.get_or_create(training=ev, user=request.user)
        rsvp.status = status
        if status == "no" and comment:
            rsvp.comment = comment
        elif status != "no":
            rsvp.comment = None  # clear previous comment if changed
        rsvp.save()
        messages.success(request, "Dein Status wurde gespeichert.")
        return redirect(request.META.get("HTTP_REFERER", reverse("team_detail_members", kwargs={"slug": slug})))

    return redirect("team_detail_members", slug=slug)

# ------------------------------------------------------------------
# Penalties / Kassenwart features
# ------------------------------------------------------------------
@login_required
def penalties_list(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not (is_player(request.user, team) or is_trainer(request.user, team) or is_cashier(request.user, team)):
        return HttpResponseForbidden("Keine Rechte für diese Ansicht.")

    penalties = Penalty.objects.filter(team=team).order_by("title")
    assigned_penalties = AssignedPenalty.objects.filter(team=team).select_related("user", "penalty").order_by("-assigned_at")
    return render(request, "teams/penalties_list.html", {
        "team": team,
        "penalties": penalties,
        "assigned_penalties": assigned_penalties,
    })

@login_required
def penalty_create(request, slug):
    team = get_object_or_404(Team, slug=slug)
    if not is_cashier(request.user, team):
        return HttpResponseForbidden("Nur Kassenwart kann Strafen-Katalog bearbeiten.")

    if request.method == "POST":
        form = PenaltyForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.team = team
            p.save()
            messages.success(request, "Strafe im Katalog hinzugefügt.")
            return redirect("penalties_list", slug=team.slug)
    else:
        form = PenaltyForm()
    return render(request, "teams/penalty_form.html", {"form": form, "team": team, "title": "Strafe erstellen"})

@login_required
def penalty_assign(request, slug, penalty_id=None, user_id=None):
    """
    Zwei Modi:
    - Wenn penalty_id übergeben: zeige Form / Zuordnung an (cashier)
    - Wenn POST mit user_id & penalty_id: erstelle AssignedPenalty
    """
    team = get_object_or_404(Team, slug=slug)
    if not is_cashier(request.user, team):
        return HttpResponseForbidden("Nur Kassenwart kann Strafen zuweisen.")

    if request.method == "POST":
        p_id = request.POST.get("penalty_id")
        u_id = request.POST.get("user_id")
        note = request.POST.get("note", "")
        penalty = get_object_or_404(Penalty, pk=p_id, team=team)
        assigned = AssignedPenalty.objects.create(
            team=team,
            user_id=u_id,
            penalty=penalty,
            note=note,
            assigned_by=request.user
        )
        messages.success(request, f"Strafe '{penalty.title}' zugewiesen.")
        return redirect("penalties_list", slug=team.slug)

    # GET: show assignment form
    penalties = Penalty.objects.filter(team=team)
    members = list(team.players.all()) + list(team.trainers.all())
    return render(request, "teams/penalty_assign_form.html", {
        "team": team,
        "penalties": penalties,
        "members": members,
    })

@login_required
def penalty_mark_paid(request, slug, assigned_id):
    team = get_object_or_404(Team, slug=slug)
    if not is_cashier(request.user, team):
        return HttpResponseForbidden("Nur Kassenwart kann Zahlungen bestätigen.")

    assigned = get_object_or_404(AssignedPenalty, pk=assigned_id, team=team)
    if request.method == "POST":
        assigned.paid = True
        assigned.save()
        messages.success(request, "Als bezahlt markiert.")
        return redirect("penalties_list", slug=team.slug)
    return render(request, "teams/confirm_delete.html", {"object": assigned, "team": team, "title": "Als bezahlt markieren?"})

def members_list(request, slug):
    team = get_object_or_404(Team, slug=slug)

    members = CustomUser.objects.filter(teams=team)

    context = {
        "team": team,
        "members": members,
    }
    return render(request, "teams/members_list.html", context)