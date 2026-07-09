# Codex workflow

## Before changes

1. Read `AGENTS.md` and the user task.
2. Check the project structure and `git status`.
3. Define the boundaries of the current stage.
4. Do not modify unrelated user files.

## During work

1. Make the smallest changes needed for the task.
2. Do not copy code from a mentor repository or another educational project.
3. Do not implement functionality from future stages early.
4. Update tests and documentation only within the scope of current changes.
5. Do not commit secrets; document new variables in `.env.example`.

## Verification

Preferred cycle:

```bash
docker compose config
docker compose up --build
docker compose exec web python manage.py check
docker compose exec web python manage.py migrate
docker compose exec web pytest
docker compose exec web flake8
```

Equivalent commands in an activated virtual environment are acceptable for local development.

## Completion

1. Review the final `git diff` and confirm there are no secrets.
2. Confirm the readiness criteria from `AGENTS.md` are met.
3. Create a local commit with the requested message when the user asks for it.
4. Do not run `git push`, add remotes, or create a GitHub repository.
