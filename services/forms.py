from django import forms

from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest

        fields = (
            "client",
            "title",
            "description",
            "status",
            "estimated_price",
        )

        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "estimated_price": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
        }
