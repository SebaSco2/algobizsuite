# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io
import json
import logging
from urllib.parse import urlencode

from odoo import http
from odoo.http import request

try:
    import qrcode
except ImportError:
    qrcode = None

try:
    from algosdk import algod
except ImportError:
    algod = None

_logger = logging.getLogger(__name__)


class AlgorandPosController(http.Controller):
    """Controller for Point of Sale Algorand payments.

    Handles:
    - QR code generation for Pera Wallet deep linking
    - Transaction verification on blockchain
    - Payment status checking
    """

    @http.route("/pos/algorand/qr_code", type="json", auth="user")
    def generate_qr_code(self, payment_method_id, amount, currency_id, order_ref):
        """Generate QR code for Algorand payment.

        Creates a QR code containing Algorand payment URI that can be scanned
        by Pera Wallet mobile app to initiate payment.

        Args:
            payment_method_id: int - POS payment method ID
            amount: float - Payment amount
            currency_id: int - Currency ID
            order_ref: str - POS order reference

        Returns:
            dict with keys:
                - qr_code: str - Base64 encoded PNG image
                - payment_uri: str - Algorand payment URI
                - merchant_address: str - Merchant's Algorand address
                - amount: float - Payment amount
                - currency: str - Currency code (ALGO or USDC)
        """
        _logger.info(
            "[Algorand][POS] QR code request: method=%s amount=%s "
            "currency=%s ref=%s",
            payment_method_id,
            amount,
            currency_id,
            order_ref,
        )

        if not qrcode:
            return {
                "error": True,
                "message": (
                    "QR code library not installed. "
                    "Please install: pip install qrcode[pil]"
                ),
            }

        try:
            # Load payment method and get Algorand data
            payment_method = (
                request.env["pos.payment.method"].sudo().browse(payment_method_id)
            )
            if not payment_method.exists():
                return {"error": True, "message": "Payment method not found"}

            currency = request.env["res.currency"].sudo().browse(currency_id)
            if not currency.exists():
                return {"error": True, "message": "Currency not found"}

            # Get Algorand payment data from payment method
            payment_data = payment_method.get_algorand_payment_data(
                amount, currency, order_ref
            )

            # Build Algorand payment URI for Pera Wallet
            # Format: algorand://pay?receiver=ADDR&amount=1000000&asset=ASSET_ID
            #         &note=ORDER_REF
            uri_params = {
                "receiver": payment_data["merchant_address"],
                "amount": payment_data["amount_microalgos"],
                "note": f"POS Order: {order_ref}",
            }

            # Add asset ID for USDC payments (0 = native ALGO)
            if payment_data["is_usdc"]:
                uri_params["asset"] = payment_data["asset_id"]

            payment_uri = f"algorand://pay?{urlencode(uri_params)}"

            _logger.info("[Algorand][POS] Generated URI: %s", payment_uri)

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(payment_uri)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            return {
                "success": True,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "payment_uri": payment_uri,
                "merchant_address": payment_data["merchant_address"],
                "amount": amount,
                "currency": payment_data["currency_code"],
                "network": payment_data["network"],
                "order_ref": order_ref,
            }

        except Exception as e:
            _logger.error(
                "[Algorand][POS] QR code generation failed: %s", e, exc_info=True
            )
            return {"error": True, "message": f"Failed to generate QR code: {str(e)}"}

    @http.route("/pos/algorand/verify_payment", type="json", auth="user")
    def verify_payment(self, tx_hash, payment_method_id, expected_amount, order_ref):
        """Verify Algorand payment on blockchain.

        Checks if a transaction with the given hash exists on the blockchain
        and validates that it matches the expected payment details.

        Args:
            tx_hash: str - Algorand transaction hash
            payment_method_id: int - POS payment method ID
            expected_amount: float - Expected payment amount
            order_ref: str - POS order reference

        Returns:
            dict with keys:
                - verified: bool - True if payment is valid
                - tx_hash: str - Transaction hash
                - amount: float - Actual payment amount
                - sender: str - Sender's Algorand address
                - confirmed_round: int - Block number where tx was confirmed
        """
        _logger.info(
            "[Algorand][POS] Verify payment: tx=%s method=%s amount=%s ref=%s",
            tx_hash,
            payment_method_id,
            expected_amount,
            order_ref,
        )

        if not algod:
            return {
                "error": True,
                "message": (
                    "Algorand SDK not installed. "
                    "Please install: pip install py-algorand-sdk"
                ),
            }

        try:
            # Load payment method
            payment_method = (
                request.env["pos.payment.method"].sudo().browse(payment_method_id)
            )
            if not payment_method.exists():
                return {"error": True, "message": "Payment method not found"}

            # Get Algorand provider config
            provider = payment_method.algorand_provider_id
            if not provider:
                return {"error": True, "message": "Algorand provider not configured"}

            # Get node URL and token from config parameters
            algod_url = (
                request.env["ir.config_parameter"].sudo().get_param("algorand.node_url")
            )
            algod_token = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("algorand.node_token", "")
            )

            if not algod_url:
                algod_url = provider.algorand_node_url

            if not algod_url:
                return {"error": True, "message": "Algorand node URL not configured"}

            _logger.info("[Algorand][POS] Connecting to node: %s", algod_url)

            # Create Algorand client
            algod_client = algod.AlgodClient(algod_token, algod_url)

            # Fetch transaction from blockchain
            try:
                tx_info = algod_client.pending_transaction_info(tx_hash)
            except Exception:
                # If not in pending, try confirmed transactions
                tx_info = algod_client.transaction_info(
                    provider.algorand_merchant_address, tx_hash
                )

            if not tx_info:
                return {"error": True, "message": "Transaction not found on blockchain"}

            _logger.info(
                "[Algorand][POS] Transaction info: %s", json.dumps(tx_info, default=str)
            )

            # Verify transaction details
            confirmed_round = tx_info.get("confirmed-round", 0)

            # Get payment details
            payment_txn = tx_info.get("txn", {}).get("txn", tx_info.get("txn", {}))

            # Check receiver address
            receiver = payment_txn.get("rcv", "")
            if receiver != provider.algorand_merchant_address:
                return {
                    "error": True,
                    "message": f"Payment sent to wrong address: {receiver}",
                }

            # Check amount
            amount_microalgos = payment_txn.get("amt", 0)
            actual_amount = amount_microalgos / 1_000_000
            expected_microalgos = int(expected_amount * 1_000_000)

            if abs(amount_microalgos - expected_microalgos) > 100:  # Allow 0.0001 diff
                return {
                    "error": True,
                    "message": (
                        f"Amount mismatch: expected {expected_amount}, "
                        f"got {actual_amount}"
                    ),
                }

            # Get sender address
            sender = payment_txn.get("snd", "")

            return {
                "verified": True,
                "tx_hash": tx_hash,
                "amount": actual_amount,
                "sender": sender,
                "confirmed_round": confirmed_round,
                "receiver": receiver,
            }

        except Exception as e:
            _logger.error(
                "[Algorand][POS] Payment verification failed: %s", e, exc_info=True
            )
            return {"error": True, "message": f"Verification failed: {str(e)}"}

    @http.route("/pos/algorand/check_transaction", type="json", auth="user")
    def check_transaction_status(self, tx_hash, payment_method_id):
        """Check transaction status on blockchain.

        Lightweight endpoint to check if a transaction has been confirmed
        without full verification.

        Args:
            tx_hash: str - Algorand transaction hash
            payment_method_id: int - POS payment method ID

        Returns:
            dict with keys:
                - confirmed: bool - True if transaction is confirmed
                - pending: bool - True if transaction is pending
                - not_found: bool - True if transaction doesn't exist
                - confirmed_round: int - Block number (if confirmed)
        """
        _logger.info(
            "[Algorand][POS] Check transaction: tx=%s method=%s",
            tx_hash,
            payment_method_id,
        )

        if not algod:
            return {"error": True, "message": "Algorand SDK not installed"}

        try:
            # Load payment method
            payment_method = (
                request.env["pos.payment.method"].sudo().browse(payment_method_id)
            )
            if not payment_method.exists():
                return {"error": True, "message": "Payment method not found"}

            # Get Algorand provider config
            provider = payment_method.algorand_provider_id
            if not provider:
                return {"error": True, "message": "Algorand provider not configured"}

            # Get node URL
            algod_url = (
                request.env["ir.config_parameter"].sudo().get_param("algorand.node_url")
            )
            algod_token = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("algorand.node_token", "")
            )

            if not algod_url:
                algod_url = provider.algorand_node_url

            if not algod_url:
                return {"error": True, "message": "Algorand node URL not configured"}

            # Create Algorand client
            algod_client = algod.AlgodClient(algod_token, algod_url)

            # Check pending transactions first
            try:
                pending_info = algod_client.pending_transaction_info(tx_hash)
                if pending_info:
                    confirmed_round = pending_info.get("confirmed-round", 0)
                    if confirmed_round > 0:
                        return {
                            "confirmed": True,
                            "pending": False,
                            "confirmed_round": confirmed_round,
                        }
                    else:
                        return {
                            "confirmed": False,
                            "pending": True,
                        }
            except Exception as e:
                _logger.debug("[Algorand][POS] Transaction not in pending pool: %s", e)
                # Not in pending, might be confirmed - check history
                pass

            # Try to fetch from confirmed transactions
            try:
                tx_info = algod_client.transaction_info(
                    provider.algorand_merchant_address, tx_hash
                )
                if tx_info:
                    return {
                        "confirmed": True,
                        "pending": False,
                        "confirmed_round": tx_info.get("confirmed-round", 0),
                    }
            except Exception as e:
                _logger.debug("[Algorand][POS] Transaction not found in history: %s", e)

            # Transaction not found
            return {
                "confirmed": False,
                "pending": False,
                "not_found": True,
            }

        except Exception as e:
            _logger.error(
                "[Algorand][POS] Transaction status check failed: %s", e, exc_info=True
            )
            return {"error": True, "message": f"Status check failed: {str(e)}"}
