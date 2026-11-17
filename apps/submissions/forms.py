from django import forms

from apps.common import BootstrapFormMixin
from apps.tools.models import Tool

from .models import ContactMessage, ToolSubmission


class ToolSubmissionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ToolSubmission
        fields = ("tool_name", "website_url", "category", "pricing_model", "short_description",
                  "description", "features", "contact_email")
        labels = {"short_description": "One-line summary", "description": "Full description",
                  "features": "Main features (one per line)"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "features": forms.Textarea(attrs={"rows": 4}),
            "website_url": forms.URLInput(attrs={"placeholder": "https://"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = True
        self.fields["category"].empty_label = "Choose a category"

    def clean_website_url(self):
        url = self.cleaned_data["website_url"].strip()
        if not url.lower().startswith("https://"):
            raise forms.ValidationError("Please use the secure https:// address of the official site.")
        if Tool.objects.filter(website_url__iexact=url).exists():
            raise forms.ValidationError("A tool with this website is already listed.")
        return url

    def clean_tool_name(self):
        name = self.cleaned_data["tool_name"].strip()
        if Tool.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A tool with this name is already listed.")
        if ToolSubmission.objects.filter(tool_name__iexact=name, status=ToolSubmission.PENDING).exists():
            raise forms.ValidationError("This tool has already been submitted and is waiting for review.")
        return name


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class NewsletterForm(forms.Form):
    email = forms.EmailField()
