from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.tools.models import Category, Tool
from apps.tools.seed_data import CATEGORIES, build_tools


class Command(BaseCommand):
    help = "Load the starter categories and AI tools. Safe to run more than once."

    def handle(self, *args, **options):
        categories = {}
        for order, (slug, name, icon, description) in enumerate(CATEGORIES, start=1):
            category, _created = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "icon": icon, "description": description, "order": order}
            )
            categories[slug] = category

        created_count = updated_count = 0
        for data in build_tools():
            values = dict(data)
            values["category"] = categories[values.pop("category")]
            slug = slugify(values["name"])
            # data_verified is only set on creation, so admins' own verification is never overwritten
            tool, created = Tool.objects.get_or_create(slug=slug, defaults={**values, "status": Tool.APPROVED})
            if created:
                created_count += 1
            else:
                updated_count += 1  # existing rows are left as they are (admins may have edited them)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {len(categories)} categories, {created_count} tools created, "
            f"{updated_count} already existed."
        ))
