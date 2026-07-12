# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Django-based French Learning Management System (LMS) — courses, paid enrollments, CEFR (A1–C2) certification exams, and a Main Admin analytics dashboard. This is `online/`, the Django project root and the git repository root (the parent `france/` directory is not itself a git repo). The full product spec this codebase is being built against lives at `../readme.txt` (one level up, outside git) — read it before adding features that touch new domain areas, since it defines the roles, workflows, and sitemap the code is meant to match.

## Commands

Python is invoked via the `py` launcher on this (Windows) machine, not `python`/`python3`.

```
py manage.py runserver 8000        # dev server
py manage.py makemigrations <app>  # after model changes, scope to the app you touched
py manage.py migrate
py manage.py shell                 # REPL; for multi-line scripts prefer:
py manage.py shell -c "exec(open(r'path\to\script.py').read())"   # avoids REPL line-by-line parsing issues with multi-line blocks (for/if) piped via stdin
py manage.py createsuperuser
py manage.py check
```

There is no `requirements.txt`/`pyproject.toml` — dependencies are whatever's installed in the active environment (Django 6.0.6, djangorestframework 3.17.1, psycopg2). Check `py -m pip list` if a fresh environment needs setting up.

There is no real automated test suite — every app's `tests.py` is the unmodified Django stub. Feature verification in this project has consistently been done manually: start the dev server, then drive the flow end-to-end with `curl` using a cookie jar (`-c cookies.txt -b cookies.txt`) for session auth, scraping the CSRF token out of rendered HTML (`grep -o 'name="csrfmiddlewaretoken" value="[^"]*"'`, double quotes matter — Django renders the attribute double-quoted), and seeding/inspecting data via one-off `manage.py shell` scripts. Follow this pattern when validating changes rather than assuming `manage.py test` covers anything. Always clean up test users/courses/payments created this way afterward, and kill the background dev server process when done (`netstat -ano | grep :8000` → `taskkill //F //PID <pid>`).

Postgres runs on a **non-default port (9999)**, not 5432 — see `online/settings.py` `DATABASES` for the full connection config.

## Architecture

**One Django app per domain concern**, matching the readme's own domain boundaries — when adding a feature, figure out which concern it belongs to before deciding where it goes:

- `web` — public marketing site: blog `Article`/`Comment`, and a `Visitor` model for feedback/newsletter-style signups. Homepage and `/articles`.
- `user` — custom `User(AbstractUser)` (`AUTH_USER_MODEL = 'user.User'`) with `role` (super_admin/main_admin/teacher/content_manager/finance/support/student) and `current_level` (A1–C2) fields. Owns login/register/logout/dashboard views. **The `role` field is set at signup but not enforced anywhere except `dashboard`'s decorator** — don't assume role-based restrictions exist elsewhere just because the field is populated.
- `courses` — `Course` → `Module` → `Lesson` content hierarchy (`LEVEL_CHOICES` A1–C2 defined here and re-imported by `certifications`). Public browsing views plus a read-only DRF `CourseViewSet` mounted at `/api/courses/`.
- `enrollments` — `Enrollment` (student↔course) and `LessonProgress`. `Enrollment.progress_percent` is a computed property (completed lessons / total lessons in the course), not a stored field — reuse it rather than recomputing progress elsewhere. Free courses (`price == 0`) enroll directly through this app; paid courses are explicitly refused here and routed to `payments`.
- `payments` — `Payment` model + a **mocked** two-step checkout→confirm→receipt flow (no real gateway/API keys anywhere in the project). `confirm_payment` is what actually activates the `Enrollment`. The two-step shape (checkout creates a pending `Payment`, a separate confirm step succeeds it) is deliberate even though it's mocked, so a real gateway can later replace just the "succeed" step.
- `certifications` — `Exam`/`Question`/`Choice` (auto-graded multiple-choice only — the readme's Writing/Speaking sections with free-response/manual grading are out of scope; `Question.section` is tagged listening/reading/writing/speaking so that can be added later without a schema change), `ExamAttempt`/`ExamAnswer`, and `Certificate` (`FR-{level}-{year}-{6-digit-seq}` IDs, publicly verifiable with no login at `/certificate/<id>/`). Exam registration mocks the certification fee the same way `payments` mocks course payment, but does *not* reuse the `Payment` model (which is hard-coupled to `Course`) — it tracks `fee_paid` directly on `ExamAttempt`.
- `dashboard` — one read-only view aggregating stats from every other app for the platform owner ("Main Admin" in the readme's terms). Gated by `main_admin_required` in `dashboard/views.py`, the only role-check decorator in the codebase — copy this pattern if more role-gated views are needed rather than inventing a new one. Deliberately separate from Django's built-in `/admin/`, which is treated as the Super Admin (developer) surface and isn't rebuilt.

**URL wiring**: each app owns a `urls.py`; `online/urls.py` includes them. Most are mounted under a prefix (`courses/`, `payments/`, `user/`) but `enrollments` (mounted at `portal/`) and `certifications`/`dashboard` (mounted at `''`) define their own full paths internally — check an app's `urls.py` directly rather than assuming its prefix from `online/urls.py` alone.

**Templates**: every page in `templates/` is a standalone, self-contained HTML document — there is no shared `{% extends %}` base template anywhere in the project. Each file has its own inline `<style>` block. The consistent visual language across all pages is navy `#050b18` background, gold `#d4af37` accent, Playfair Display (headings) + Inter (body) fonts — match this exactly when adding pages rather than introducing a new style.

**Migration history note**: `AUTH_USER_MODEL` was swapped to `user.User` after the project already had `admin`/`auth` migrations applied against Django's built-in `auth.User`, which is normally unsafe. The dev database was fully reset to resolve it (acceptable pre-launch, no real user data existed). Don't repeat a bare `AUTH_USER_MODEL` swap against a database with real data without a reset plan.
