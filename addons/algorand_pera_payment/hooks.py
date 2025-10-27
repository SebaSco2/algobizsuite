# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    """Post-install hook to ensure payment methods are created and linked."""
    # Get the payment provider
    provider = env["payment.provider"].search([("code", "=", "algorand_pera")], limit=1)

    if provider:
        # Ensure default payment methods exist for the provider
        codes = provider._get_default_payment_method_codes() or []
        for code in codes:
            method = env["payment.method"].search([("code", "=", code)], limit=1)
            if method and method not in provider.payment_method_ids:
                provider.write({"payment_method_ids": [(4, method.id)]})

        # Ensure account.payment.method is linked to the provider's journal
        if provider.journal_id:
            account_payment_method = env["account.payment.method"].search(
                [("code", "=", "algorand_pera"), ("payment_type", "=", "inbound")],
                limit=1,
            )

            if account_payment_method:
                # Check if the payment method line already exists
                existing_line = env["account.payment.method.line"].search(
                    [
                        ("journal_id", "=", provider.journal_id.id),
                        ("payment_method_id", "=", account_payment_method.id),
                    ],
                    limit=1,
                )

                if not existing_line:
                    # Create the payment method line
                    env["account.payment.method.line"].create(
                        {
                            "journal_id": provider.journal_id.id,
                            "payment_method_id": account_payment_method.id,
                        }
                    )

        # Note: Journal assignment is handled by Odoo's standard payment flow
