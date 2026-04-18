# HorizonBI Delivery Notes

## 1. High-level architecture summary
HorizonBI is a modular Django project organized by business domain instead of one flat app list. It uses a custom user model, Django Groups/Permissions, property-scoped access helpers, service/selectors layers for analytics and report access, Tailwind-friendly Django templates, and a Power BI app-owned embed scaffold.

## 2. Recommended project structure
- `config/` — split settings, root URLs, ASGI/WSGI
- `apps/core/` — shared models, access helpers, UI context, security event logging
- `apps/usermanagement/` — users, roles, profiles
- `apps/properties/` — organizations, properties, property switching
- `apps/dashboard/` — dashboard landing page
- `apps/analytics/` — KPI models, calculations, dashboard builders, filters, views, template tags
- `apps/powerbi/` — report groups, reports, embed token service scaffold, access selectors
- `apps/dataops/` — file lifecycle monitoring, ingestion/load history, download audit
- `apps/notifications/` — notifications and announcements
- `apps/settings/mappings/` — property-scoped hospitality mapping domains and segmentation hierarchy

## 3. ZIP-ready installable project file tree
See `PROJECT_TREE.txt` for the expanded tree.

## 4. Django models
Key model entry points:
- `apps/usermanagement/users/models.py`
- `apps/usermanagement/profiles/models.py`
- `apps/properties/core/models.py`
- `apps/analytics/kpi/models.py`
- `apps/powerbi/embedded/models.py`
- `apps/dataops/files/models.py`
- `apps/settings/mappings/models/`

## 5. Permissions and access-control design
Property-scoped access and role checks are centralized in:
- `apps/core/common/access.py`
- `apps/usermanagement/roles/services.py`
- `apps/powerbi/embedded/selectors.py`
- `apps/dataops/files/selectors.py`

Views, forms, querysets, and navigation all consume the same access helpers.

## 6. Forms
Primary form layers:
- `apps/usermanagement/users/forms.py`
- `apps/usermanagement/profiles/forms.py`
- `apps/analytics/kpi/forms.py`
- `apps/dataops/files/forms.py`
- `apps/notifications/announcements/forms.py`
- `apps/settings/mappings/forms/`

## 7. Views
Primary view layers:
- `apps/dashboard/home/views.py`
- `apps/usermanagement/users/views.py`
- `apps/usermanagement/profiles/views.py`
- `apps/analytics/kpi/views.py`
- `apps/powerbi/embedded/views.py`
- `apps/dataops/files/views.py`
- `apps/settings/mappings/views/`

## 8. URL configuration
- Root: `config/urls.py`
- Auth: `apps/usermanagement/users/auth_urls.py`
- Domain URLs live inside each app and are mounted at root.

## 9. Tailwind-based template structure
- Base layout: `templates/base.html`
- Shared partials: `templates/partials/`
- Cards/components: `templates/components/`
- Domain-specific pages: `templates/dashboard/`, `templates/analytics/`, `templates/powerbi/`, `templates/dataops/`, `templates/settings/mappings/`, `templates/users/`

## 10. Example templates
Representative files:
- Navbar: `templates/partials/navbar.html`
- Sidebar: `templates/partials/sidebar.html`
- Breadcrumbs: `templates/partials/breadcrumbs.html`
- Login: `templates/registration/login.html`
- Dashboard: `templates/dashboard/home/index.html`
- Notifications: `templates/notifications/inbox_list.html`
- User management: `templates/users/list.html`, `templates/users/form.html`
- Profile: `templates/users/profile.html`, `templates/users/profile_form.html`

## 11. Power BI embed scaffolding
- Models: `apps/powerbi/embedded/models.py`
- Access selectors: `apps/powerbi/embedded/selectors.py`
- Embed service: `apps/powerbi/embedded/services.py`
- Views/templates: `apps/powerbi/embedded/views.py`, `templates/powerbi/`

## 12. Data and file management scaffolding
- Models: `apps/dataops/files/models.py`
- Selectors/services: `apps/dataops/files/selectors.py`, `apps/dataops/files/services.py`
- Views/templates: `apps/dataops/files/views.py`, `templates/dataops/`

## 13. Hospitality dashboards and KPI engine
- KPI formulas: `apps/analytics/kpi/services/kpi_calculations.py`
- Dashboard builders: `apps/analytics/kpi/services/dashboard_builders.py`
- Template tags/formatters: `apps/analytics/kpi/templatetags/`
- Analytics templates: `templates/analytics/`

## 14. Django management commands for demo data
Included commands:
- `seed_roles`
- `seed_properties`
- `seed_demo_users`
- `seed_analytics_demo`
- `seed_notifications_demo`
- `seed_powerbi_demo`
- `seed_dataops_demo`
- `seed_mapping_demo`
- `seed_segmentation_demo`
- `seed_all_demo`

## 15. README with installation and setup commands
See `README.md`.

## 16. Production hardening recommendations
- Use `config.settings.prod`
- Set secure cookies and HSTS via environment
- Build Tailwind CSS locally and disable the browser CDN
- Replace SQLite with PostgreSQL through `DATABASE_URL`
- Wire SMTP/SES or another real email backend
- Add object-level audit events where required
- Add a cache layer and background workers for token refresh, imports, and notifications

## 17. Next steps for expansion into a full SaaS platform
- Introduce tenant isolation at organization level
- Add subscription/billing plans around report-group and property entitlements
- Add async ingestion pipelines and scheduled jobs
- Add granular object-level permissions and approval workflows
- Expand Power BI token caching and report-view analytics
- Add API/webhook ingestion endpoints and import schedulers
