# HorizonBI

HorizonBI is a modular Django admin dashboard and analytics application for hotels, restaurants, and hospitality groups. It includes authentication, role-based and property-based access control, dashboard analytics, data/file operations, Power BI embedded reporting scaffolding, notifications, announcements, and a full settings mapping domain for hospitality code normalization.

## What is included

- Custom user model with property assignments and role-aware UI
- Dashboard landing page with KPI cards, analytics charts, quick links, and recent activity
- Tailwind-based templates with dark/light mode support
- Analytics dashboards for executive overview, occupancy, revenue, property performance, and goals
- Power BI embed scaffold using app-owned embedding and backend token generation
- DataOps module for missing/received/loaded/downloaded file monitoring
- Notifications and announcements center
- Settings > Mappings module with segmentation hierarchy and property-scoped mapping CRUD
- Demo seed commands for major modules

## Project structure

```text
manage.py
requirements.txt
pyproject.toml
.env.example
README.md
package.json
tailwind.config.js
config/
apps/
templates/
static/
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_all_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/accounts/login/`

## Tailwind workflow

For the quickest local demo, templates can use the Tailwind browser build when `TAILWIND_USE_CDN=True` in `.env`. This is a development convenience only. Tailwind recommends using the install/CLI flow for production builds rather than the browser CDN.

To compile Tailwind locally for production-style usage:

```bash
npm install
npm run build:css
```

Then set `TAILWIND_USE_CDN=False` in `.env` (or use `config.settings.prod`, which already forces the CDN off).

## Demo users

After `seed_all_demo`, the following demo users are created with password `DemoPass123!`:

- `admin@horizonbi.local`
- `manager@horizonbi.local`
- `operator@horizonbi.local`
- `merchant@horizonbi.local`
- `viewer@horizonbi.local`

## Demo seed commands

```bash
python manage.py seed_roles
python manage.py seed_properties
python manage.py seed_demo_users
python manage.py seed_analytics_demo
python manage.py seed_notifications_demo
python manage.py seed_powerbi_demo
python manage.py seed_dataops_demo
python manage.py seed_mapping_demo
python manage.py seed_segmentation_demo
python manage.py seed_all_demo
```

## Power BI configuration

Populate the following values in `.env` to enable embedding:

- `POWERBI_TENANT_ID`
- `POWERBI_CLIENT_ID`
- `POWERBI_CLIENT_SECRET`
- `POWERBI_SCOPE`
- `POWERBI_API_BASE_URL`
- `POWERBI_AUTHORITY_URL`

Without these values the embedded report page will render a safe configuration warning instead of exposing secrets.

## Key access-control principles

- Django authentication is required for all protected pages.
- Roles are seeded into Django Groups.
- Property assignments restrict access to dashboard data, users, reports, files, and mappings.
- Views, querysets, forms, and navigation all enforce property-scoped access.
- Power BI report access is validated server-side before token generation.
- File downloads are permission-gated and recorded in audit history.

## Mapping domains

The Settings > Mappings area includes:

- Market segmentation (groups, categories, segments, details)
- Room type
- Package
- Rate code
- Travel agent
- Guest country
- Company
- Day of week
- Booking source
- Origin
- Competitor
- Loyalty

## Deployment notes

- Default database configuration is SQLite for local setup via `DATABASE_URL`.
- The project is ready to move to PostgreSQL by changing the `DATABASE_URL`.
- WhiteNoise is enabled for static file serving.
- `config/settings/` provides split settings for development and production.
- Review secure cookie, host, and SSL settings before deployment.
