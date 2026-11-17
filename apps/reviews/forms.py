from django import forms

from apps.common import BootstrapFormMixin

from .models import Review

RATING_CHOICES = [(5, "5 - Excellent"), (4, "4 - Good"), (3, "3 - Okay"), (2, "2 - Poor"), (1, "1 - Bad")]


class ReviewForm(BootstrapFormMixin, forms.ModelForm):
    rating = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)

    class Meta:
        model = Review
        fields = ("rating", "title", "body")
        widgets = {"body": forms.Textarea(attrs={"rows": 4, "placeholder": "What did you use it for? What worked well?"})}

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if len(body) < 10:
            raise forms.ValidationError("Please write at least 10 characters.")
        return body
