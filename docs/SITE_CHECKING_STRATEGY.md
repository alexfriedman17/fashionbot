# Site Checking Strategy

Last updated: 2026-04-12

## Principle

Use the simplest and fastest method that can prove the status without guessing.

Preferred order:

1. Exact vendor API or embedded product data.
2. Plain HTTP page fetch and structured-data parsing.
3. Bundled Playwright Chromium with a project-owned browser profile.
4. MCP/browser-control tools such as Blueprint only when configured and needed for manual-style browsing.
5. `manual_check` if the page is blocked, blank, ambiguous, or requires a human-controlled session.

Never use the user's personal Chrome profile for scheduled checks.

## Current Site Matrix

| Site | Current Best Method | Why | Fallback | Notes |
| --- | --- | --- | --- | --- |
| Topologie | Playwright first, then consider Shopify product JSON/HTTP | Bundled Chromium currently sees explicit sold-out and add-to-cart signals. Topologie may also expose Shopify-style product data. | `manual_check` if variant selection is unclear or page blocks. | For Bungee Wrist Strap, either Mint or Sleet can satisfy the watch item. |
| LEGO | Playwright first | The size menu is rendered as button/option text after page load, so the checker needs browser-rendered button labels. | `manual_check` if target sizes M8/M9/M10 are missing or the page blocks. | Wait 3 seconds after load and dismiss the retail/games destination popup if it appears. |
| Coach / Coachtopia | HTTP/HTML first | Bundled Playwright Chromium has produced blank pages for Coach, while page-readable content can expose `Add to Bag`, `Buy Now`, or `Sold Out`. | Playwright only as a secondary proof attempt; otherwise `manual_check`. | Prefer canonical product URLs when known, for example `CFF99.html` over tracking/variant URLs that fail to render. |
| Poshmark | Not in v1 | Poshmark checks were intentionally deferred. | Require explicit Poshmark item or saved-search URLs before adding. | Do not infer exact matches from broad search snippets. |

## HTTP-First Rules

Use HTTP or embedded product data when:

- The target page returns product title, price, availability, variant, or structured JSON in the response.
- The needed signal is explicit, such as `Sold Out`, `Out of Stock`, `Add to Bag`, or `Buy Now`.
- The item does not require clicking through a variant selector that only exists after JavaScript rendering.

Do not use HTTP output when:

- The page is a search result, recommendation, or unrelated canonical redirect.
- It only shows generic marketing copy or product images.
- It omits the target variant or size.
- It returns a bot challenge, blank page, or ambiguous shell.

## Playwright Rules

Use bundled Playwright Chromium when:

- The site requires JavaScript to render product controls.
- The relevant signal is visible only in buttons, selectors, modals, or menus.
- A site-specific popup can be dismissed safely without choosing a purchase action.

Keep Playwright conservative:

- Use `.browser-profile/`, not the user's normal Chrome profile.
- Use exact product URLs only.
- Keep checks low-volume.
- Mark blank, blocked, or ambiguous pages as `manual_check`.

## Blueprint MCP Rules

Blueprint MCP is not active in this project yet.

Use Blueprint only after:

- The Blueprint MCP server is registered with the agent host.
- The browser extension is installed and connected.
- A VM or agent runtime can operate it reliably without the user's personal browser profile.

Blueprint should be treated as a browser-control backend, not as a replacement for faster HTTP checks. Use it when a human-like browser session is genuinely required and the operational setup is available.

## Evidence Requirements

Every site checker should return a compact proof object:

- Final URL.
- Status: `available`, `sold_out`, or `manual_check`.
- Status reason.
- Relevant button labels or structured availability fields.
- Timestamp.
- Screenshot path only when a browser proof is useful.

If the evidence does not prove the target item, variant, or size, return `manual_check`.
