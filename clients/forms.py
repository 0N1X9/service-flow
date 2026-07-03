from django import forms

from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client

        fields = (
            "name",
            "email",
            "phone",
            "company",
            "notes",
        )

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "company": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }
