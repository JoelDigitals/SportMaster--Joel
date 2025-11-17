# core/views.py
from django.shortcuts import render
from django.db.models import Q
from team.models import Team
from club.models import Club

def home(request):
    """
    Öffentliche Startseite:
    - Sportarten-Menü (distinct)
    - Letzte Teams
    - Optional: Meine Teams, falls eingeloggt
    """
    sports = Team.objects.values_list("sport", flat=True).distinct().order_by("sport")
    latest_teams = Team.objects.select_related("club", "age_group")[:12]

    my_teams = None
    if request.user.is_authenticated:
        my_teams = request.user.teams.select_related("club", "age_group")

    context = {
        "sports": sports,
        "latest_teams": latest_teams,
        "my_teams": my_teams,
    }
    return render(request, "core/home.html", context)


def sport_overview(request, sport_name):
    """
    Zeigt alle Teams einer bestimmten Sportart.
    """
    teams = (
        Team.objects.filter(sport__iexact=sport_name)
        .select_related("club", "age_group")
        .order_by("club__name", "name")
    )

    context = {
        "sport_name": sport_name,
        "teams": teams,
    }
    return render(request, "core/sport_overview.html", context)


def search(request):
    """
    Universelle Suchseite:
    - Suche nach Teams
    - Suche nach Clubs
    """
    query = request.GET.get("q", "")

    teams = []
    clubs = []

    if query:
        teams = (
            Team.objects.filter(
                Q(name__icontains=query)
                | Q(club__name__icontains=query)
                | Q(sport__name__icontains=query)        # FIX
                | Q(age_group__name__icontains=query)
            )
            .select_related("club", "age_group", "sport")
            .order_by("name")
        )

        clubs = (
            Club.objects.filter(
                Q(name__icontains=query)
                | Q(address__icontains=query)
            )
            .order_by("name")
        )

    context = {
        "query": query,
        "teams": teams,
        "clubs": clubs,
    }

    return render(request, "core/search.html", context)
