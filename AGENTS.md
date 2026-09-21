# Novacode Project Instructions

Use this file to override or extend the default agent behavior for this project.

## General Rules
- Prefer minimal diffs over rewrites.
- Run the relevant linter and tests before finalizing changes.
- Do not hardcode secrets; load them from environment variables or `.env`.
- Use absolute paths for configuration references when possible.
- Keep changes backward compatible unless explicitly asked to break compatibility.
- Default to action: implement, refactor, debug, and deliver runnable outputs.

## Model Resolution
- Default model: `nexus-think:latest` (local Ollama).
- Stack 100% offline: modelos propios `novacode-*` en Ollama.
- Proveedores API (Nvidia/Anthropic) deshabilitados por defecto; habilitar en `providers.json` si se obtienen keys válidas.

## MCP Services
- Filesystem MCP is scoped to `/Users/djkoveck/Projects`, `/Users/djkoveck/Developer`, `/Users/djkoveck/clones`, and `/Users/djkoveck`.
- Git MCP is available via `pipx run mcp-server-git`.
- Do not install new MCP servers without explicit instruction.

## Agent Selection
- Default agent: `code`
- For read-only exploration, use `explore`.
- For CI/build tasks, use `build`.
- For planning, use `plan`.
- For multimodal tasks, use `multimodal`.
- For general assistance, use `general`.
- For large changes, prefer a short plan first, then execute in small verifiable steps.

## Error Handling
- If a command fails, read the error output, diagnose, and fix.
- If a fix fails twice, report the blocker and stop.
- Do not retry blindly.
