# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json
import logging

from odoo.addons.payment import utils as payment_utils
from .. import const

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('algorand_pera', 'Algorand Pera Wallet')],
        ondelete={'algorand_pera': 'set default'}
    )
    
    algorand_merchant_address = fields.Char(
        string="Merchant Algorand Address",
        help="The Algorand address that will receive payments",
    )
    
    algorand_network = fields.Selection([
        ('testnet', 'Testnet'),
        ('mainnet', 'Mainnet')
    ], string="Algorand Network", default='testnet', required=True)
    
    algorand_node_url = fields.Char(
        string="Algorand Node URL",
        default="https://testnet-api.algonode.cloud",
        help="The Algorand node URL for transaction broadcasting"
    )

    # Add logo field for provider
    image_128 = fields.Image(
        string="Logo",
        help="The logo displayed for this payment provider",
        max_width=128,
        max_height=128,
    )

    # Note: No provider-specific accounting/journal fields
    # Odoo's standard payment flow handles journal assignment automatically

    def _get_supported_currencies(self, *args, **kwargs):
        """ Override to return the supported currencies. """
        if self.code == 'algorand_pera':
            # Algorand supports USD (via USDC stablecoin)
            # Return USD currency explicitly to ensure it's always available
            return self.env['res.currency'].search([('name', '=', 'USD')])
        return super()._get_supported_currencies(*args, **kwargs)

    def _get_supported_flows(self):
        """ Override to return the supported payment flows. """
        if self.code == 'algorand_pera':
            return ['direct']
        return super()._get_supported_flows()

    def _get_default_payment_method_codes(self):
        """ Override to return the default payment method codes. """
        self.ensure_one()
        if self.code != 'algorand_pera':
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    def _algorand_get_inline_form_values(
        self, amount, currency, partner_id, is_validation, payment_method_sudo=None, **kwargs
    ):
        """Return a serialized JSON of the required values to render the inline form.

        Note: `self.ensure_one()`

        :param float amount: The amount in major units, to convert in minor units.
        :param res.currency currency: The currency of the transaction.
        :param int partner_id: The partner of the transaction, as a `res.partner` id.
        :param bool is_validation: Whether the operation is a validation.
        :param payment.method payment_method_sudo: The sudoed payment method record to which the
                                                   inline form belongs.
        :return: The JSON serial of the required values to render the inline form.
        :rtype: str
        """
        self.ensure_one()
        
        # Decide if we should use USDC ASA (when user currency is USD)
        use_usdc = bool(currency and currency.name == 'USD')
        usdc_asset_id = const.USDC_ASA_IDS_BY_NETWORK.get(self.algorand_network) if use_usdc else None
        currency_display_name = 'USDC' if use_usdc else (currency.name if currency else 'ALGO')

        # Use provider-level merchant address (no method-level override)
        merchant_address = self.algorand_merchant_address

        # Try to include a recent pending transaction id for this partner/provider to help finalize
        tx_id_val = None
        try:
            if partner_id:
                tx = self.env['payment.transaction'].sudo().search([
                    ('partner_id', '=', partner_id),
                    ('provider_code', '=', 'algorand_pera'),
                    ('state', 'in', ('draft', 'pending', 'authorized')),
                ], order='create_date desc', limit=1)
                if tx:
                    tx_id_val = tx.id
        except Exception:
            tx_id_val = None

        inline_form_values = {
            'tx_id': tx_id_val,
            'merchant_address': merchant_address,
            'amount': amount,
            'currency_name': currency.name if currency else 'ALGO',
            'currency_display_name': currency_display_name,
            'partner_id': partner_id,
            'is_validation': is_validation,
            'network': self.algorand_network,
            'node_url': self.algorand_node_url,
            'payment_methods_mapping': const.PAYMENT_METHODS_MAPPING,
            'is_asa': use_usdc,
            'asset_id': usdc_asset_id,
            'asset_decimals': const.USDC_DECIMALS if use_usdc else 6,
        }
        
        return json.dumps(inline_form_values)

    def _send_payment_request(self, tx_sudo):
        """ Override to handle Algorand Pera Wallet payment requests. """
        if self.code != 'algorand_pera':
            return super()._send_payment_request(tx_sudo)
        
        # For Algorand Pera Wallet, we don't send a request to an external provider
        # The payment is handled entirely on the frontend
        tx_sudo.write({'state': 'pending'})
        return None

    # === VALIDATION === #
    
    @api.constrains('algorand_merchant_address', 'algorand_network')
    def _check_algorand_merchant_address(self):
        """Validate that merchant address is set and properly formatted."""
        for provider in self:
            if provider.code != 'algorand_pera':
                continue
            
            # Only validate if provider is enabled or test mode
            if provider.state in ('enabled', 'test'):
                if not provider.algorand_merchant_address:
                    raise ValidationError(_(
                        "Merchant Algorand Address is required to enable the payment provider. "
                        "Please configure your Algorand wallet address in the provider settings."
                    ))
                
                # Validate address format (basic check)
                address = provider.algorand_merchant_address.strip()
                if len(address) != 58:
                    raise ValidationError(_(
                        "Invalid Algorand address format. "
                        "Algorand addresses must be exactly 58 characters long."
                    ))
    
    def _check_algorand_usdc_optin(self):
        """Check if merchant address is opted-in to USDC asset."""
        self.ensure_one()
        if self.code != 'algorand_pera':
            return True
        
        if not self.algorand_merchant_address:
            return False
        
        try:
            from algosdk.v2client import algod
            
            # Get USDC asset ID for current network
            usdc_asset_id = const.USDC_ASA_IDS_BY_NETWORK.get(self.algorand_network)
            if not usdc_asset_id:
                _logger.warning(
                    "No USDC asset ID configured for network %s", 
                    self.algorand_network
                )
                return False
            
            # Query blockchain for account info
            algod_client = algod.AlgodClient('', self.algorand_node_url)
            account_info = algod_client.account_info(self.algorand_merchant_address)
            
            # Check if account is opted-in to USDC
            assets = account_info.get('assets', [])
            for asset in assets:
                asset_id = asset.get('asset-id', 0)
                if asset_id == usdc_asset_id:
                    _logger.info(
                        "Merchant address %s is opted-in to USDC (asset %s) on %s",
                        self.algorand_merchant_address[:10] + '...',
                        usdc_asset_id,
                        self.algorand_network
                    )
                    return True
            
            _logger.warning(
                "Merchant address %s is NOT opted-in to USDC (asset %s) on %s",
                self.algorand_merchant_address[:10] + '...',
                usdc_asset_id,
                self.algorand_network
            )
            return False
            
        except ImportError:
            _logger.error("algosdk not installed, cannot verify USDC opt-in")
            return False
        except Exception as e:
            _logger.error(
                "Failed to check USDC opt-in for address %s: %s",
                self.algorand_merchant_address[:10] + '...' if self.algorand_merchant_address else 'None',
                str(e)
            )
            return False
    
    # === ADMIN ACTIONS === #
    
    def action_algorand_verify_node(self):
        self.ensure_one()
        if self.code != 'algorand_pera':
            return {'type': 'ir.actions.act_window_close'}
        url = self.algorand_node_url or 'https://testnet-api.algonode.cloud'
        message = f"Node URL configured: {url}"
        level = 'info'
        try:
            # Try a lightweight status call if sdk is available
            from algosdk.v2client import algod  # type: ignore
            client = algod.AlgodClient('', url)
            _ = client.status()  # may raise
            message = f"Algorand node reachable: {url}"
            level = 'success'
        except Exception as e:  # pragma: no cover
            level = 'warning'
            message = f"Could not reach Algorand node: {url} ({e})"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': level,
                'sticky': False,
            },
        }

    def action_algorand_check_usdc_optin(self):
        """Check if merchant address is opted-in to USDC and display notification."""
        self.ensure_one()
        if self.code != 'algorand_pera':
            return {'type': 'ir.actions.act_window_close'}
        
        if not self.algorand_merchant_address:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Please configure the Merchant Algorand Address first."),
                    'type': 'warning',
                    'sticky': False,
                },
            }
        
        is_opted_in = self._check_algorand_usdc_optin()
        usdc_asset_id = const.USDC_ASA_IDS_BY_NETWORK.get(self.algorand_network, 'N/A')
        
        if is_opted_in:
            message = _(
                "✓ Merchant address is opted-in to USDC (Asset ID: %s) on %s. "
                "You can accept USD payments."
            ) % (usdc_asset_id, self.algorand_network.upper())
            msg_type = 'success'
        else:
            message = _(
                "✗ Merchant address is NOT opted-in to USDC (Asset ID: %s) on %s. "
                "Please opt-in to accept USD payments. "
                "You can still accept ALGO payments."
            ) % (usdc_asset_id, self.algorand_network.upper())
            msg_type = 'warning'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': msg_type,
                'sticky': True,
            },
        }
    
    def action_toggle_is_published(self):
        """Toggle the published state of the payment provider."""
        self.ensure_one()
        self.is_published = not self.is_published
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }