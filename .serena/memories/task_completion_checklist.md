# Task Completion Checklist
1. Run `uv run poe fix` (format + lint) and ensure it passes.
2. Run targeted `uv run poe test` or relevant subset; confirm green.
3. Verify new/changed public functions have type hints and Google-style docstrings.
4. Check Loguru logging usage and environment variable handling for new code.
5. Update or add tests/docs when behavior changes.
6. Prepare Conventional Commit message summarizing changes (Japanese summary + bullet list of modifications).