# Browser Backends

## Playwright

`playwright` is the working local CLI backend.

For per-site backend choice, use `docs/SITE_CHECKING_STRATEGY.md` as the source of truth.

Use it for local hourly checks and manual dry runs:

```powershell
python -m fashionbot check --dry-run --recap --headless
python -m fashionbot check --recap
```

Headed mode is the default. It uses a project-owned persistent `.browser-profile/` directory. Do not use the user's personal Chrome profile for scheduled checks.

## Blueprint MCP

`blueprint` is reserved for a future MCP-backed browser flow. It is not available to the Python process by itself.

Before this backend can run, the agent host needs a Blueprint MCP server and a connected browser extension:

- Install Node.js.
- Add the MCP server to the agent host with `npx @railsblueprint/blueprint-mcp@latest`.
- Install the Blueprint MCP browser extension.
- Open the extension and connect the current browser tab to the MCP server.

The CLI currently fails fast with setup guidance when called with:

```powershell
python -m fashionbot check --browser blueprint
```

Once Blueprint MCP is registered in the agent host, add a dedicated integration layer that calls the MCP tools instead of Playwright.
