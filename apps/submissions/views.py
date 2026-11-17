from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ContactForm, NewsletterForm, ToolSubmissionForm
from .models import NewsletterSubscriber


@login_required
def submit_tool(request):
    form = ToolSubmissionForm(request.POST or None, initial={"contact_email": request.user.email})
    if request.method == "POST" and form.is_valid():
        submission = form.save(commit=False)
        submission.submitted_by = request.user
        submission.save()
        messages.success(request, "Thanks! Your tool was submitted and is waiting for review.")
        return redirect("accounts:dashboard")
    return render(request, "submit.html", {"form": form})


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Message sent. Thank you for getting in touch.")
        return redirect("submissions:contact")
    return render(request, "contact.html", {"form": form})


@require_POST
def newsletter_signup(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        _subscriber, created = NewsletterSubscriber.objects.get_or_create(email=form.cleaned_data["email"].lower())
        messages.success(request, "You're on the list!" if created else "That email is already subscribed.")
    else:
        messages.error(request, "Please enter a valid email address.")
    # Go back to the page the form was on, but only if it is a safe local URL
    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = "/"
    return redirect(next_url)
