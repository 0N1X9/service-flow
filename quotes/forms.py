from django import forms

from .models import Quote


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = [
            "content",
            # "price",
        ]

        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 16,
                    "class": "form-control",
                }
            )
        }
