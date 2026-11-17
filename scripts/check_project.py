"""
Offline sanity checks that do NOT need Django installed.
Run:  python scripts/check_project.py

Checks: template tags are balanced, every {% url %} / reverse() / redirect() name exists, {% static %} files exist,
{% extends %} / {% include %} targets exist, and every element id used by the JavaScript exists in a template.
(These checks cannot replace running the site - see README "Testing".)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []

# ------------------------------------------------------------------ URL names
url_names = {"admin:index", "admin:login", "admin:logout"}
for urls_file in ROOT.glob("apps/*/urls.py"):
    text = urls_file.read_text(encoding="utf-8")
    ns = re.search(r'app_name\s*=\s*"(\w+)"', text)
    for name in re.findall(r'name="(\w+)"', text):
        url_names.add(f"{ns.group(1)}:{name}" if ns else name)
config = (ROOT / "config/urls.py").read_text(encoding="utf-8")
for name in re.findall(r'name="(\w+)"', config):
    url_names.add(name)
ADMIN_PATTERN = re.compile(r"^admin:\w+_\w+_(changelist|add|change)$")


def known_url(name):
    return name in url_names or bool(ADMIN_PATTERN.match(name))


# ------------------------------------------------------------------ templates
OPEN = {"if", "for", "block", "with", "autoescape", "comment"}
templates = list((ROOT / "templates").rglob("*"))
templates = [t for t in templates if t.is_file()]
all_template_text = ""
for path in templates:
    text = path.read_text(encoding="utf-8")
    all_template_text += text
    rel = path.relative_to(ROOT / "templates")
    stack = []
    for match in re.finditer(r"{%\s*(\w+)(.*?)%}", text, re.S):
        tag, rest = match.group(1), match.group(2)
        if tag in OPEN:
            stack.append(tag)
        elif tag.startswith("end") and tag[3:] in OPEN:
            if not stack or stack[-1] != tag[3:]:
                errors.append(f"{rel}: unexpected {{% {tag} %}} (stack={stack})")
            else:
                stack.pop()
        elif tag == "url":
            m = re.match(r"\s*['\"]([\w:]+)['\"]", rest)
            if m and not known_url(m.group(1)):
                errors.append(f"{rel}: unknown url name '{m.group(1)}'")
        elif tag == "static":
            m = re.match(r"\s*['\"]([^'\"]+)['\"]", rest)
            if m and not (ROOT / "static" / m.group(1)).exists():
                errors.append(f"{rel}: missing static file '{m.group(1)}'")
        elif tag in ("extends", "include"):
            m = re.match(r"\s*['\"]([^'\"]+)['\"]", rest)
            if m and not (ROOT / "templates" / m.group(1)).exists():
                errors.append(f"{rel}: missing template '{m.group(1)}'")
        elif tag in ("load", "csrf_token", "elif", "else", "empty", "url"):
            pass
    if stack:
        errors.append(f"{rel}: unclosed tags {stack}")
    if text.count("{{") != text.count("}}"):
        errors.append(f"{rel}: unbalanced {{{{ }}}}")

# render() targets exist
for py in ROOT.glob("apps/*/views.py"):
    text = py.read_text(encoding="utf-8")
    for tpl in re.findall(r'render\(\s*request,\s*"([^"]+)"', text):
        if not (ROOT / "templates" / tpl).exists():
            errors.append(f"{py.relative_to(ROOT)}: render() template missing: {tpl}")
    for name in re.findall(r'(?:redirect|reverse)\(\s*"([\w:]+)"', text):
        if not known_url(name):
            errors.append(f"{py.relative_to(ROOT)}: unknown url name '{name}'")
for py in list(ROOT.glob("apps/*/models.py")) + list(ROOT.glob("apps/*/admin.py")) + list(ROOT.glob("config/settings.py")):
    for name in re.findall(r'reverse\(\s*"([\w:]+)"', py.read_text(encoding="utf-8")):
        if not known_url(name):
            errors.append(f"{py.relative_to(ROOT)}: unknown url name '{name}'")
for lazy in re.findall(r'reverse_lazy\(\s*"([\w:]+)"', (ROOT / "apps/accounts/urls.py").read_text(encoding="utf-8")):
    if not known_url(lazy):
        errors.append(f"accounts/urls.py: unknown url name '{lazy}'")
for setting in re.findall(r'(?:LOGIN_URL|LOGIN_REDIRECT_URL|LOGOUT_REDIRECT_URL)\s*=\s*"([\w:]+)"', (ROOT / "config/settings.py").read_text(encoding="utf-8")):
    if not known_url(setting):
        errors.append(f"settings: unknown url name '{setting}'")

# ------------------------------------------------------------------ JS ids
for js in (ROOT / "static/js").glob("*.js"):
    text = js.read_text(encoding="utf-8")
    for ident in set(re.findall(r"getElementById\('([\w-]+)'\)", text)):
        has_id = f'id="{ident}"' in all_template_text or f'json_script:"{ident}"' in all_template_text
        if not has_id:
            errors.append(f"{js.name}: element id '{ident}' not found in any template")

# ------------------------------------------------------------------ result
print(f"Checked {len(templates)} templates, {len(url_names)} named URLs.")
if errors:
    print("PROBLEMS FOUND:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("All static checks passed.")
