# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    algorand_tx_id = fields.Char(
        string="Algorand Transaction ID",
        help="The transaction ID returned by the Algorand network",
    )

    algorand_sender_address = fields.Char(
        string="Sender Algorand Address",
        help="The Algorand address that sent the payment",
    )

    algorand_network = fields.Selection(
        selection=[
            ("testnet", "Testnet"),
            ("mainnet", "Mainnet"),
        ],
        string="Algorand Network",
        help="Network on which the Algorand payment was performed",
    )

    def _get_specific_processing_values(self, processing_values):
        """Override of payment to return Algorand-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic processing values of the
            transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        if self.provider_code != "algorand_pera":
            return super()._get_specific_processing_values(processing_values)

        # For Algorand Pera Wallet, return processing values for inline form
        return {
            "tx_id": self.id,
            "merchant_address": self.provider_id.algorand_merchant_address,
            "amount_algo": self.amount,
            "currency": self.currency_id.name,
            "order_id": self.reference,
        }

    # === Transaction Processing Methods === #
    # These methods override Odoo's standard payment flow to handle
    # Algorand-specific data

    def _extract_amount_data(self, payment_data):
        """Extract amount and currency from payment data.

        For Algorand, we trust the transaction record's amount rather than
        parsing external data, since the blockchain transaction has already
        been validated.
        """
        if self.provider_code != "algorand_pera":
            return super()._extract_amount_data(payment_data)
        return {
            "amount": self.amount,
            "currency_code": self.currency_id.name,
        }

    def _apply_updates(self, payment_data):
        """Update transaction record with Algorand blockchain data.

        This is called by _process() after payment confirmation.
        It extracts the blockchain transaction ID and sender address,
        stores them, and marks the transaction as done.

        Note: Post-processing (account.payment creation, invoice
        reconciliation) is handled by Odoo's standard cron job, not here.
        This prevents race conditions and database conflicts.
        """
        if self.provider_code != "algorand_pera":
            return super()._apply_updates(payment_data)

        # Extract blockchain transaction data (use standardized field name 'tx_id')
        tx_hash = payment_data.get("tx_id")
        sender = payment_data.get("sender_address")

        if not tx_hash:
            _logger.error(
                "[Algorand][tx] Missing tx_id in payment_data for ref=%s",
                self.reference,
            )
            raise ValueError("Missing transaction ID in payment data")

        _logger.info(
            "[Algorand][tx] _apply_updates called ref=%s txid=%s sender=%s "
            "state(before)=%s",
            self.reference,
            tx_hash,
            sender,
            self.state,
        )

        # Store blockchain transaction details
        if tx_hash:
            self.provider_reference = tx_hash
            self.algorand_tx_id = tx_hash
        if sender:
            self.algorand_sender_address = sender

        # Algorand transactions are immediately confirmed on-chain
        # Mark transaction as done to trigger post-processing
        self._set_done()
        _logger.info(
            "[Algorand][tx] _apply_updates set done ref=%s txid=%s state(after)=%s",
            self.reference,
            tx_hash,
            self.state,
        )

        return None

    @api.model
    def _search_by_reference(self, provider_code, payment_data):
        """Find transaction by merchant reference (order number).

        This is used by _process() to locate the correct transaction record
        when receiving payment confirmation from the frontend.
        """
        if provider_code != "algorand_pera":
            return super()._search_by_reference(provider_code, payment_data)
        reference = payment_data.get("reference")
        if reference:
            tx = self.search(
                [
                    ("reference", "=", reference),
                    ("provider_code", "=", "algorand_pera"),
                ]
            )
        else:
            tx = self
        if not tx:
            _logger.warning(
                "No Algorand transaction found matching reference %s.", reference
            )
        return tx

    def _process_notification_data(self, provider_code, notification_data):
        """Override to process the notification data sent by the provider."""
        if provider_code != "algorand_pera":
            return super()._process_notification_data(provider_code, notification_data)

        # Extract transaction data from notification
        tx_id = notification_data.get("tx_id")
        sender_address = notification_data.get("sender_address")

        if tx_id:
            self.write(
                {
                    "algorand_tx_id": tx_id,
                    "algorand_sender_address": sender_address,
                    "state": "done",
                }
            )
            _logger.info("Algorand payment confirmed: %s", tx_id)
        else:
            self.write({"state": "error"})
            _logger.error("Algorand payment failed: no transaction ID")

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Override to find the transaction based on the notification data."""
        if provider_code != "algorand_pera":
            return super()._get_tx_from_notification_data(
                provider_code, notification_data
            )

        # Find transaction by reference
        reference = notification_data.get("reference")
        if reference:
            return self.search(
                [
                    ("reference", "=", reference),
                    ("provider_code", "=", "algorand_pera"),
                ]
            )
        return self.browse()

    def _execute_callback(self):
        """Override to execute the callback after the payment."""
        if self.provider_code != "algorand_pera":
            return super()._execute_callback()

        # Execute the callback for Algorand payments
        super()._execute_callback()
