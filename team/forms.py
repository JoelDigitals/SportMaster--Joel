from django import forms
from .models import Team, Lineup, TrainingSeries, TrainingEvent, Message, Penalty

class LineupForm(forms.ModelForm):
    class Meta:
        model = Lineup
        fields = ["name", "date", "players", "is_public"]
        widgets = {
            "players": forms.CheckboxSelectMultiple,
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class TrainingSeriesForm(forms.ModelForm):
    class Meta:
        model = TrainingSeries
        fields = ["weekday", "time", "start_date", "end_date"]
        widgets = {
            "time": forms.TimeInput(attrs={"type": "time"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

class TrainingEventForm(forms.ModelForm):
    class Meta:
        model = TrainingEvent
        fields = ["start", "location", "note"]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            "name",
            "club",
            "age_group",
            "sport",
            "players",
            "trainers",
            "short_code",
            "additional_info",
        ]
        widgets = {
            "players": forms.CheckboxSelectMultiple,
            "trainers": forms.CheckboxSelectMultiple,
        }

class PenaltyForm(forms.ModelForm):
    class Meta:
        model = Penalty
        fields = ["title", "amount", "description"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "z. B. Zuspätkommen"
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.50",
                "placeholder": "z. B. 2.50"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional: Beschreibung der Strafe"
            }),
        }

        labels = {
            "title": "Titel",
            "amount": "Betrag (€)",
            "description": "Beschreibung (optional)",
        }