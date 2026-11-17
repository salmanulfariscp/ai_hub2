from django import forms

from apps.common import BootstrapFormMixin

from .models import Category
from .recommender import BUDGETS, PROFESSIONS, PURPOSES


class RecommendationForm(forms.Form):
    """Validates the quiz answers sent by the recommendation page (GET parameters)."""

    purpose = forms.ChoiceField(choices=[(v, label) for v, label, _i, _c in PURPOSES])
    profession = forms.ChoiceField(choices=[(v, label) for v, label, _i, _c in PROFESSIONS])
    budget = forms.ChoiceField(choices=[(v, label) for v, label, _i in BUDGETS])
    prefer_free = forms.ChoiceField(choices=[("yes", "Yes"), ("no", "No preference")])
    category = forms.ChoiceField(required=False)
    interests = forms.CharField(required=False, max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [("", "No preference")] + [(c.slug, c.name) for c in Category.objects.all()]
