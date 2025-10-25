# Style and Conventions
- Follow PEP 8 with Ruff enforcing formatting/linting; keep lines ~79 chars.
- All functions/classes require type hints and Google-style docstrings (Args/Returns/Raises) when public.
- Prefer descriptive identifiers; avoid unnecessary abstraction and keep functions focused (<20 lines when possible).
- Write self-explanatory code, comment only to explain *why*; use Loguru for logging.
- For tests, place under `tests/` mirroring module structure; target deterministic pytest cases covering happy path and edge conditions.
- Security: no eval/exec on user input, close resources properly, read config via environment variables.