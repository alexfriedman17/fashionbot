# Product PRD: Fashion Availability Agent

## Goal

Build a simple local agent that checks selected fashion items across original brand websites and reports when availability status changes.

## V1 Scope

- Read a single structured source of truth from `watchlist.json`.
- Check original vendor product URLs only.
- Use exact product or variant URLs, not broad search snippets.
- Classify each target as `available`, `sold_out`, or `manual_check`.
- Generate `watchlist.md` as a readable mirror of the JSON state.
- Print concise local summaries grouped by status.

## Out Of Scope For V1

- Poshmark checks.
- Auto-purchase flows.
- Price guessing.
- Variant guessing.
- Captcha, Cloudflare, or anti-bot bypassing.
- Email, SMS, Slack, or Discord notifications.
- Multi-user accounts or hosted dashboard.

## Availability Rules

- Mark `available` only when the live original vendor page explicitly shows that the target item or variant can be purchased.
- Mark `sold_out` only when the live original vendor page explicitly shows sold-out, out-of-stock, unavailable, or equivalent status.
- Mark `manual_check` when the page is blocked, challenged, ambiguous, missing stock UI, redirects unexpectedly, or otherwise cannot be classified without guessing.

## Initial Watchlist

| ID | Brand | Product | Variant Target | Size | Price Target | URL |
| --- | --- | --- | --- | --- | --- | --- |
| topologie-bomber-strap | Topologie | Bomber Strap | Any | n/a | $75 | https://topologie.com/products/bomber-strap |
| topologie-scrunchie-pocket-wrist | Topologie | Scrunchie Pocket Wrist | Any | n/a | $82 | https://topologie.com/products/scrunchie-pocket-wrist |
| topologie-bungee-wrist-strap | Topologie | Bungee Wrist Strap | Sleet (Tech Sateen) OR Mint (Tech Sateen) | n/a | $45 | Multiple exact URLs |
| coach-small-slouchy-patchwork | Coachtopia / Coach | Small Slouchy Shoulder Bag In Upcrafted Patchwork | Unknown | Unknown | Unknown | https://www.coach.com/products/coachtopia/small-slouchy-shoulder-bag-in-upcrafted-patchwork/CFF99-Z6Q.html |
| coach-alterego-slouchy-leather | Coachtopia / Coach | Alter/Ego Slouchy Shoulder Bag In Upcrafted Leather | Unknown | Unknown | Unknown | https://www.coach.com/products/coachtopia/alterego-slouchy-shoulder-bag-in-upcrafted-leather/CBE00.html |

## Output Expectations

Each run should produce a concise local summary:

- Group by `Available`, `Manual check`, and `Sold out`.
- Include item name, source, purchase link, status, notes, and timestamp.
- Only report status changes by default.
- Report all items when `--recap` is passed.

## Success Criteria

- The checker can read `watchlist.json` and update each item without losing existing fields.
- Availability is never inferred from incomplete evidence.
- `watchlist.json` and generated `watchlist.md` remain aligned.
- Blocked or unclear pages are marked `manual_check`.
- Re-running without status changes does not create noisy updates unless recap mode is used.
