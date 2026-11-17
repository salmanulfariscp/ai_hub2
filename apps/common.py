"""Small helpers shared by several apps."""
from django import forms
from django.utils.text import slugify


def unique_slug(model, text, max_length=140):
    """Return a slug for `text` that no other row of `model` is using yet."""
    base = slugify(text)[: max_length - 6] or "item"
    slug, counter = base, 2
    while model.objects.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug


class BootstrapFormMixin:
    """Adds Bootstrap 5 CSS classes to every widget so forms look right.

    Put it BEFORE the Django form class:  class MyForm(BootstrapFormMixin, forms.Form)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, forms.Select):  # also covers SelectMultiple
                css_class = "form-select"
            else:
                css_class = "form-control"
            widget.attrs["class"] = (widget.attrs.get("class", "") + " " + css_class).strip()
