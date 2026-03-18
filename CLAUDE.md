# CLAUDE.md

**Read [AGENTS.md](AGENTS.md) first** — it contains the full project context: architecture, data flow, entity model, API documentation, development commands, and known gotchas.

This file contains only Claude Code-specific instructions. Project context additions or edits belong in `AGENTS.md`, not here.

## Dependencies

All `homeassistant.*` imports can be assumed to exist at runtime — do not attempt to install or verify them locally. The integration runs inside Home Assistant which provides these packages.
