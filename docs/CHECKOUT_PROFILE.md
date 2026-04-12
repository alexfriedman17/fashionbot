# Checkout Profile

The checkout profile gives a future checkout assistant enough non-card context to prepare an order after an item becomes available.

## Files

- `checkout_profile.example.json`: tracked example schema for collaborators.
- `checkout_profile.local.json`: local private profile file, ignored by git.

## Payment Boundary

Do not store full credit card numbers, CVV codes, or account passwords in either checkout profile file.

Use one of these safer payment approaches instead:

- A saved payment method in the vendor account.
- A browser wallet or password-manager autofill inside the persistent browser profile.
- A tokenized payment profile ID from a compliant payment provider.
- Manual confirmation at checkout before the order is placed.

It is acceptable to store a masked payment reference such as a payment label and last four digits so the user can recognize the intended payment method.

## Required Purchase Controls

The first checkout flow should keep these defaults:

- `require_confirmation_before_purchase`: `true`
- `allow_auto_submit_order`: `false`
- `checkout_target`: `final_review_before_place_order`
- `payment_entry`: `manual_or_saved_wallet_only`

The bot may add an available target item to cart, enter shipping details, and navigate to the final review step when the site allows it without raw card entry. It must stop before final purchase submission. If a site requires raw card or CVV entry to reach final review, the bot should pause for manual payment entry or use an already-saved wallet/payment profile.
