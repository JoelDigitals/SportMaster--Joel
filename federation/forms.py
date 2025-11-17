from django import forms
from .models import Head_Federation, Federation


class HeadFederationForm(forms.ModelForm):
    class Meta:
        model = Head_Federation
        fields = [
            "name",
            "parent",
            "country",
            "contact_email",
            "adress",
            "phone_number",
            "website",
            "additional_info",
        ]


class FederationForm(forms.ModelForm):
    class Meta:
        model = Federation
        fields = [
            "name",
            "parent",
            "head_federation",
            "country",
            "contact_email",
            "adress",
            "phone_number",
            "website",
            "additional_info",
        ]
