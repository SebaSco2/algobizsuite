/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

console.log('[Algorand][POS] ==================== MODULE LOADED ====================');
console.log('[Algorand][POS] PaymentScreen:', PaymentScreen);

// Patch the PaymentScreen to intercept Algorand payments
console.log('[Algorand][POS] Applying patch...');
patch(PaymentScreen.prototype, {
    async addNewPaymentLine(paymentMethod) {
        console.log('[Algorand][POS] ==================== addNewPaymentLine CALLED ====================');
        console.log('[Algorand][POS] Payment method data:', {
            id: paymentMethod.id,
            name: paymentMethod.name,
            is_algorand: paymentMethod.is_algorand_pera,
            has_provider: paymentMethod.algorand_provider_id,
            all_keys: Object.keys(paymentMethod)
        });
        
        // Check if this is an Algorand payment method
        if (paymentMethod.is_algorand_pera || paymentMethod.algorand_provider_id) {
            console.log('[Algorand][POS] Algorand payment detected!');
            await this._handleAlgorandPayment(paymentMethod);
            return;
        }
        
        // Call original method for non-Algorand payments
        return await super.addNewPaymentLine(...arguments);
    },
    
    async _handleAlgorandPayment(paymentMethod) {
        console.log('[Algorand][POS] Handling Algorand payment');
        const order = this.pos.get_order();
        const amount = order.get_due();
        const currency = this.pos.currency;
        const orderRef = order.name || order.uid;
        
        // First, add the payment line (calls the original POS method)
        await super.addNewPaymentLine(paymentMethod);
        
        try {
            // Then generate QR code
            console.log('[Algorand][POS] Calling QR code endpoint...');
            const result = await this.env.services.rpc('/pos/algorand/qr_code', {
                payment_method_id: paymentMethod.id,
                amount: amount,
                currency_id: currency.id,
                order_ref: orderRef,
            });
            
            console.log('[Algorand][POS] QR generated:', result);
            
            if (result.error) {
                this.env.services.notification.add(result.message, { type: 'danger' });
                return;
            }
            
            // Show notification with QR code info
            this.env.services.notification.add(
                `Algorand Payment: Scan QR code with Pera Wallet. Amount: ${amount} ${currency.name}`,
                { type: 'info', sticky: true }
            );
            
            console.log('[Algorand][POS] Payment URI:', result.payment_uri);
            
        } catch (error) {
            console.error('[Algorand][POS] Error:', error);
            this.env.services.notification.add(
                `Error generating Algorand QR code: ${error.message}`,
                { type: 'danger' }
            );
        }
    }
});

console.log('[Algorand][POS] Patch applied successfully!');

