# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PeraPaymentController(http.Controller):
    
    @http.route('/payment/algorand_pera/form', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def algorand_pera_form(self, **kwargs):
        """Display the Algorand Pera Wallet payment form."""
        _logger.info('[Algorand][algorand_pera_form] CALLED with kwargs=%s', list(kwargs.keys()))
        
        # Get the payment transaction
        tx_id = kwargs.get('tx_id')
        reference = kwargs.get('reference')
        
        if not tx_id or not reference:
            return request.redirect('/shop')
        
        tx = request.env['payment.transaction'].sudo().browse(int(tx_id))
        if not tx.exists() or tx.reference != reference:
            return request.redirect('/shop')
        
        # Get the provider
        provider = tx.provider_id
        if provider.code != 'algorand_pera':
            return request.redirect('/shop')
        
        # Prepare the rendering values
        rendering_values = {
            'tx': tx,
            'provider': provider,
            'merchant_address': provider.algorand_merchant_address,
            'amount_algo': tx.amount,
            'currency': tx.currency_id.name,
            'order_id': tx.reference,
        }
        
        _logger.info('[Algorand][algorand_pera_form] RETURNING payment form for tx_id=%s reference=%s', tx_id, reference)
        return request.render('algorand_pera_payment.payment_form', rendering_values)
    
    @http.route('/payment/algorand_pera/process', type='json', auth='public', csrf=False)
    def algorand_pera_process(self, **kwargs):
        """
        Process the Algorand payment after blockchain confirmation.
        
        ENTRY POINT: Called by frontend after blockchain transaction is broadcast
        
        This is called by the frontend after the user signs and broadcasts
        the transaction via Pera Wallet. It receives the transaction hash
        and updates the payment.transaction record.
        
        Flow:
        1. Validate payment data from frontend
        2. Update transaction record using _process()
        3. Monitor transaction for /payment/status page
        4. Confirm the associated sale order
        5. Save session to ensure state is persisted
        6. Return success to trigger frontend redirect
        """
        _logger.info('[Algorand][algorand_pera_process] ==================== CALLED ====================')
        
        tx_id = kwargs.get('tx_id')
        tx_hash = kwargs.get('tx_hash')
        sender_address = kwargs.get('sender_address')
        error_message = kwargs.get('error_message')

        _logger.info('[Algorand][algorand_pera_process] Payload: tx_id=%s tx_hash=%s sender=%s error=%s', tx_id, tx_hash, sender_address, error_message)
        
        # Handle error cases from frontend
        if error_message:
            if 'overspend' in error_message.lower():
                return {
                    'error': True,
                    'message': 'Insufficient funds. Please add more ALGO to your wallet to complete this payment.',
                    'type': 'insufficient_funds'
                }
            else:
                return {
                    'error': True,
                    'message': 'Payment failed. Please try again or contact support if the problem persists.',
                    'type': 'payment_error'
                }
        
        # Validate required payment data
        if not tx_id or not tx_hash:
            return {'error': True, 'message': 'Missing transaction data'}
        
        # Load the payment transaction record
        tx = request.env['payment.transaction'].sudo().browse(int(tx_id))
        if not tx.exists():
            return {'error': True, 'message': 'Transaction not found'}

        try:
            _logger.info('[Algorand][process] Tx record: reference=%s amount=%s currency=%s provider=%s', tx.reference, tx.amount, tx.currency_id and tx.currency_id.name, tx.provider_code)
        except Exception as e:
            _logger.warning('[Algorand][process] Failed to log tx record: %s', e)
        
        # Process the transaction using Odoo's standard payment flow
        # This updates transaction state and triggers payment creation
        data = {
            'reference': tx.reference,
            'tx_id': tx_hash,
            'sender_address': sender_address,
        }
        tx.sudo()._process('algorand_pera', data)
        
        # Register transaction for monitoring on /payment/status page
        # This stores the tx ID in session so the status page can display it
        from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
        PaymentPostProcessing.monitor_transaction(tx)
        _logger.info('[Algorand][process] Transaction %s monitored for /payment/status', tx.id)
        
        # Note: Accounting entries (account.payment, invoices) are NOT created here
        # They are handled by Odoo's post-processing cron and provider settings

        # Confirm the associated sale order
        so_id = request.session.get('sale_order_id')
        if so_id:
            order = request.env['sale.order'].sudo().browse(int(so_id)).exists()
            if order and order.state in ('draft', 'sent'):
                try:
                    order.action_confirm()
                    # Add payment confirmation to order chatter
                    order.message_post(body=f"Algorand payment confirmed. tx_id={tx_hash}")
                    _logger.info('[Algorand] Order %s confirmed successfully', order.name)
                except Exception as e:
                    _logger.warning('[Algorand] Order confirmation failed: %s', e)

        # Cart clearing is handled automatically by Odoo's website_sale module:
        # - When order is confirmed (state changes from 'draft' to 'sale')
        # - User navigates to /shop or /shop/cart
        # - website_sale controller detects order.state != 'draft'
        # - session['sale_order_id'] is set to None
        # - Cart badge updates via page reload
        #
        # Manual cart clearing can cause issues:
        # - Race conditions with multiple tabs/windows
        # - Session synchronization problems
        # - Interference with Odoo's built-in cart management

        _logger.info('[Algorand][algorand_pera_process] ==================== SUCCESS ====================')
        return {'success': True, 'tx_id': tx_hash}


