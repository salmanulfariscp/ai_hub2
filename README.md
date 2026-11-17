# AI HUB - AI Tools Discovery Platform

A Django web application for discovering, comparing and saving AI tools. It grew out of the original
HTML/CSS/Bootstrap "AI HUB" site: the name, the sky-blue accent, Poppins font, hero video and category idea are kept,
and the site now has a real backend, database, user accounts and an admin area.

**Stack (only what the project brief allows):** HTML5, CSS3, Bootstrap 5, JavaScript, Bootstrap Icons, Python, Django, MySQL, Git/GitHub.
No React / Vue / Angular / Node / TypeScript / Tailwind.

---

## 1. One-time software you need

| Software | Why | Check it |
|---|---|---|
| Python 3.10 or newer | runs Django | `python --version` |
| Git (optional) | version control | `git --version` |
| MySQL 8 (optional) | production database. **Not needed to try the site** - SQLite is the default | `mysql --version` |

## 2. Quick start (SQLite, no database server needed)

Open a terminal in the project folder (the one containing `manage.py`).

**Windows:** run `setup.bat`  **macOS / Linux:** run `bash setup.sh`

These scripts do exactly the commands below. You can also type them yourself:

```bash
# Windows                         # macOS / Linux
python -m venv venv               python3 -m venv venv
venv\Scripts\activate             source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            cp .env.example .env
python manage.py makemigrations accounts tools favorites reviews submissions
python manage.py migrate
python manage.py seed_data        # loads 9 categories and 53 tools
python manage.py createsuperuser  # your admin login (choose your own username/password)
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser. Admin: **http://127.0.0.1:8000/admin/** (statistics page: `/manage/`).

> **Why `makemigrations`?** Migration files describe database tables. They are created from `models.py` on your computer
> the first time (step 4 above). After that, commit the new `apps/*/migrations/0001_initial.py` files to Git.

## 3. Using MySQL instead of SQLite

1. Install MySQL 8 and start it.
2. Create the database and a user (replace the password):
   ```sql
   CREATE DATABASE ai_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'ai_hub_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
   GRANT ALL PRIVILEGES ON ai_hub.* TO 'ai_hub_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. Edit `.env`:
   ```
   DB_ENGINE=mysql
   DB_NAME=ai_hub
   DB_USER=ai_hub_user
   DB_PASSWORD=choose-a-strong-password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
4. Run `python manage.py makemigrations accounts tools favorites reviews submissions`, `python manage.py migrate` and `python manage.py seed_data` again.

The driver is **PyMySQL** (pure Python, installs on Windows without a compiler). `.env` is ignored by Git, so passwords never reach GitHub.

## 4. What is in the project

| Page | URL | Notes |
|---|---|---|
| Home | `/` | hero + live search suggestions, categories, popular, featured, trending, recent, free, recommended, newsletter |
| Explore | `/explore/` | real-time search, category pills, pricing + open-source filters, sorting, pagination, skeleton loading, no-results state |
| Categories | `/categories/`, `/category/<slug>/` | the 9 categories; each opens the explorer locked to that category |
| Tool details | `/tools/<slug>/` | one template for every tool: logo, features, pros/cons, use cases, pricing, similar tools, reviews, bookmark, compare, add to collection |
| Compare | `/compare/` | 2-3 tools side by side; shareable link `?tools=chatgpt,claude` |
| Recommendations | `/recommendations/` | 5-question quiz, ranked by simple rules in `apps/tools/recommender.py` (no paid API) |
| Favorites | `/favorites/` | guests: localStorage. Logged-in users: database. Guest bookmarks are copied to the account on login |
| Auth | `/accounts/login/`, `register/`, `password-reset/`, `profile/`, `password-change/` | Django's built-in auth (hashed passwords, CSRF, sessions, validators) |
| Dashboard | `/accounts/dashboard/` | profile, favourites, recently viewed, collections, reviews, submissions, recommendations |
| Submit a tool | `/submit/` | login required; validated; goes to an approval queue |
| About / Contact | `/about/`, `/contact/` | contact messages are saved and visible in admin |
| Admin | `/admin/`, `/manage/` | Django admin for add/edit/delete tools, categories, users, reviews; approve submissions; feature tools. `/manage/` shows statistics |

### Folder structure
```
AI-HUB/
├── manage.py  requirements.txt  README.md  .env.example  .gitignore  setup.bat  setup.sh
├── config/                  settings.py (reads .env), urls.py
├── apps/
│   ├── accounts/            Profile model, register / profile / dashboard / staff statistics
│   ├── tools/               Category, Tool, RecentlyViewed; home, explore, details, compare, recommender, JSON API, seed data
│   ├── favorites/           Favorite and Collection models; AJAX toggle
│   ├── reviews/             Review model (1-5 stars)
│   └── submissions/         ToolSubmission, ContactMessage, NewsletterSubscriber
├── templates/               base.html, one template per page, partials/ for reusable pieces
├── static/css/              style.css (main), responsive.css (breakpoints)
├── static/js/               main.js, filters.js, cards.js, search.js, compare.js, favorites.js, recommendations.js
├── static/video/hero.mp4    your original hero video
├── scripts/check_project.py offline checker (templates, URL names, static files)
└── tests/                   test_filters.js (Node) ; apps/tools/tests.py (Django tests)
```
(Categories live inside the `tools` app because a category is only a label on a tool - one app fewer to learn.)

### Database relationships (the important part to understand)
- **Category 1 → many Tool** (`Tool.category` is a `ForeignKey`). Deleting a category that still has tools is blocked (`PROTECT`).
- **User ↔ Tool through Favorite**: a many-to-many relation with its own table; `unique_together` stops duplicates.
- **Tool 1 → many Review**, **User 1 → many Review**; one review per user per tool.
- **User 1 → 1 Profile** (`OneToOneField`), created automatically by a signal (`apps/accounts/signals.py`).
- **Collection** belongs to one user and holds many tools (`ManyToManyField`).
- **ToolSubmission**: when an admin approves one, a `Tool` is created and linked back.

## 5. Data honesty
- Descriptions are short and general. Pricing is only **free / freemium / paid** - **no prices, ratings or user counts are invented**.
- Every seeded tool has `data_verified = False` and shows an "Unverified details" badge. Check the official site, then tick *data verified* in the admin.
- "Featured" and "Trending" are **editorial flags** you set in the admin, not measured statistics.
- Ratings appear only after real users write reviews.
- Logos are fetched at view time from Google's favicon service and fall back to the tool's initial if unavailable (needs internet).

## 6. Admin tasks
- **Add / edit / delete a tool:** Admin → Tools. **Feature it:** tick *is featured* or use the bulk action.
- **Approve a submission:** Admin → Tool submissions → select → action *Approve selected submissions*. It is published immediately.
- **Hide a review:** Admin → Reviews → untick *is approved* (or use the bulk action).
- **Users:** Admin → Users. **Statistics:** `/manage/` (staff only).

## 7. Git and GitHub
```bash
git init
git add .
git commit -m "AI HUB: Django version"
git branch -M main
git remote add origin https://github.com/<your-username>/ai-hub.git
git push -u origin main
```
`.gitignore` already excludes `.env`, `venv/`, `db.sqlite3` and caches.

## 8. Testing
```bash
python manage.py test                # Django tests (pages, API, favourites, registration, reviews)
node tests/test_filters.js           # search/filter/sort/pagination logic (Node.js needed)
python scripts/check_project.py      # template tags, URL names, static files
```

## 9. Features needing extra configuration
- **MySQL** - see section 3 (SQLite works out of the box).
- **Password-reset email** - in development the email is printed in the terminal running `runserver`. For real email set `EMAIL_BACKEND` and the SMTP values in `.env`.
- **Newsletter** - addresses are stored (visible in admin). The project does not send newsletters.
- **Production** - set `DJANGO_DEBUG=False`, a long random `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_HTTPS=True`, then run `python manage.py collectstatic` and serve with a proper web server. The hero video needs static-file serving configured there.
- **Internet** is needed for Bootstrap, Bootstrap Icons and Google Fonts (loaded from CDNs) and for tool logos.

## 10. Known limitations
- Recommendations use transparent rules, not machine learning.
- Explore/Compare load the whole tool list as JSON (fine for hundreds of tools; use server-side pagination if it grows to thousands).
- Reviews are published immediately; admins can hide them afterwards.
- No tool screenshots: the detail page shows a labelled illustration instead of invented images.
