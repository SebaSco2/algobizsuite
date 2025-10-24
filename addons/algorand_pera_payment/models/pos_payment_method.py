# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    """
    Extend POS payment methods to support Algorand Pera Wallet payments.
    
    This model links the payment.provider (used for e-commerce) to the
    pos.payment.method (used in Point of Sale). When a payment provider
    with code 'algorand_pera' is configured, it can be used as a POS
    payment method that generates QR codes for Pera Wallet scanning.
    """
    _inherit = 'pos.payment.method'

    # Link to the Algorand payment provider
    algorand_provider_id = fields.Many2one(
        'payment.provider',
        string='Algorand Provider',
        domain=[('code', '=', 'algorand_pera')],
        help='The Algorand payment provider to use for this POS payment method'
    )
    
    # Flag to identify if this is an Algorand payment method
    is_algorand_pera = fields.Boolean(
        string='Is Algorand Pera Wallet',
        compute='_compute_is_algorand_pera',
        store=True
    )
    
    @api.depends('algorand_provider_id')
    def _compute_is_algorand_pera(self):
        """Compute if this payment method uses Algorand"""
        for method in self:
            method.is_algorand_pera = bool(method.algorand_provider_id)
    
    def _load_pos_data_fields(self, config_id):
        """Add Algorand-specific fields to POS session data"""
        result = super()._load_pos_data_fields(config_id)
        result += ['algorand_provider_id', 'is_algorand_pera']
        return result

    @api.model
    def create_from_algorand_provider(self, provider):
        """
        Create a POS payment method from an Algorand payment provider.
        
        This method is called during provider setup to automatically create
        a corresponding POS payment method.
        
        Args:
            provider: payment.provider record with code='algorand_pera'
            
        Returns:
            pos.payment.method record
        """
        if provider.code != 'algorand_pera':
            return False
            
        # Check if POS payment method already exists
        existing = self.search([
            ('algorand_provider_id', '=', provider.id)
        ], limit=1)
        
        if existing:
            _logger.info('[Algorand][POS] Payment method already exists: %s', existing.name)
            return existing
        
        # Create new POS payment method
        vals = {
            'name': f'Algorand - {provider.name}',
            'algorand_provider_id': provider.id,
            'company_id': provider.company_id.id,
        }
        
        method = self.create(vals)
        _logger.info('[Algorand][POS] Created payment method: %s (ID: %s)', method.name, method.id)
        return method

    def get_algorand_payment_data(self, amount, currency, order_ref):
        """
        Get Algorand payment data for QR code generation.
        
        This method fetches the necessary data from the linked payment provider
        to generate a payment QR code that Pera Wallet can scan.
        
        Args:
            amount: float - Payment amount
            currency: res.currency - Currency record
            order_ref: str - POS order reference
            
        Returns:
            dict with keys:
                - merchant_address: str - Algorand address to receive payment
                - amount_microalgos: int - Amount in microalgos (for ALGO)
                - asset_id: int - Asset ID for USDC payments (0 for ALGO)
                - network: str - 'testnet' or 'mainnet'
                - node_url: str - Algorand node URL
                - currency_code: str - Currency code (ALGO or USDC)
                - order_ref: str - Order reference for transaction note
        """
        if not self.algorand_provider_id:
            raise ValueError('No Algorand provider configured for this payment method')
        
        provider = self.algorand_provider_id
        
        # Validate provider is enabled
        if provider.state not in ('enabled', 'test'):
            raise ValueError(f'Algorand provider is not enabled (state: {provider.state})')
        
        # Get merchant address
        merchant_address = provider.algorand_merchant_address
        if not merchant_address:
            raise ValueError('Merchant address not configured in Algorand provider')
        
        # Get network and node URL
        network = provider.algorand_network or 'testnet'
        node_url = provider.algorand_node_url
        
        # Determine if this is USDC or ALGO payment
        is_usdc = currency.name == 'USD' and provider.algorand_use_usdc
        
        if is_usdc:
            # USDC payment (Asset transfer)
            asset_id = int(provider.algorand_usdc_asset_id or 0)
            if not asset_id:
                raise ValueError('USDC asset ID not configured in Algorand provider')
            
            # USDC has 6 decimals
            amount_microunits = int(amount * 1_000_000)
            currency_code = 'USDC'
        else:
            # ALGO payment (Native token)
            asset_id = 0
            # ALGO has 6 decimals (microalgos)
            amount_microunits = int(amount * 1_000_000)
            currency_code = 'ALGO'
        
        return {
            'merchant_address': merchant_address,
            'amount_microalgos': amount_microunits,
            'asset_id': asset_id,
            'network': network,
            'node_url': node_url,
            'currency_code': currency_code,
            'order_ref': order_ref,
            'is_usdc': is_usdc,
        }


class PaymentProvider(models.Model):
    """
    Extend payment provider to automatically create POS payment methods.
    """
    _inherit = 'payment.provider'

    def write(self, vals):
        """
        When an Algorand provider is enabled, automatically create a POS payment method.
        """
        result = super().write(vals)
        
        # If provider is being enabled and it's Algorand, create POS payment method
        if vals.get('state') in ('enabled', 'test'):
            for provider in self:
                if provider.code == 'algorand_pera':
                    self.env['pos.payment.method'].sudo().create_from_algorand_provider(provider)
        
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """
        When an Algorand provider is created and enabled, automatically create a POS payment method.
        """
        providers = super().create(vals_list)
        
        for provider in providers:
            if provider.code == 'algorand_pera' and provider.state in ('enabled', 'test'):
                self.env['pos.payment.method'].sudo().create_from_algorand_provider(provider)
        
        return providers

