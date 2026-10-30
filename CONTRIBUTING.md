# Contributing
## Branching
main is protected; work on feature/* or fix/* and open a PR; every PR needs 1 review + green CI.
## Commits
Use prefixes: feat:, fix:, docs:, test:, ci:.
## Before pushing
pytest -q && bandit -r app.py -ll
