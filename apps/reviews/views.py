from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from apps.tools.models import Tool

from .forms import ReviewForm
from .models import Review


@login_required
@require_POST
def submit_review(request, slug):
    """Create the user's review for a tool, or update it if they already wrote one."""
    tool = get_object_or_404(Tool.objects.approved(), slug=slug)
    existing = Review.objects.filter(tool=tool, user=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.tool = tool
        review.user = request.user
        review.save()
        messages.success(request, "Your review was saved.")
    else:
        problems = "; ".join(error for errors in form.errors.values() for error in errors)
        messages.error(request, f"Review not saved: {problems}")
    return redirect(tool.get_absolute_url() + "#reviews")


@login_required
@require_POST
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user and not request.user.is_staff:
        messages.error(request, "You can only delete your own reviews.")
        return redirect("tools:home")
    tool = review.tool
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect(tool.get_absolute_url() + "#reviews")
