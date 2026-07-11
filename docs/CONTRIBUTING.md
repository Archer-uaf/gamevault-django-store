# Contributing to GameVault

GameVault is an educational Django/DRF project. Contributions should stay focused, preserve the existing architecture, and keep public behavior covered by tests.

## Before making changes

1. Review the current project structure and `git status`.
2. Define the boundaries of the change and avoid unrelated edits.
3. Do not commit secrets, local databases, generated static files, virtual environments, or editor settings.
4. Document new environment variables in `.env.example`.

## Implementation guidelines

1. Prefer small, testable changes over broad rewrites.
2. Keep business rules in services or models rather than templates.
3. Reuse shared behavior between the web and API layers.
4. Add or update tests when public behavior changes.
5. Keep Ukrainian as the source UI language and update English gettext translations for user-facing strings.

## Verification

Run the relevant focused tests first, followed by the complete project checks in Docker:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web pytest
docker compose exec web flake8
docker compose exec web mypy .
docker compose exec web python manage.py spectacular --validate --file /tmp/schema.yml
git diff --check
```

Before committing, review the final diff, confirm that no secrets or generated files were added, and make sure documentation describes only implemented behavior.
