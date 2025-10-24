/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class AlgorandPaymentPopup extends Component {
    static template = "algorand_pera_payment.AlgorandPaymentPopup";
    
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.state = {
            qrCode: null,
            loading: true,
            error: null,
            paymentUri: null,
        };
        this.generateQRCode();
    }
    
    async generateQRCode() {
        try {
            const { amount, currency, orderRef, paymentMethodId } = this.props;
            
            console.log('[Algorand][Popup] Generating QR code...', { amount, currency, orderRef, paymentMethodId });
            
            const result = await this.rpc('/pos/algorand/qr_code', {
                payment_method_id: paymentMethodId,
                amount: amount,
                currency_id: currency.id,
                order_ref: orderRef,
            });
            
            if (result.error) {
                this.state.error = result.message;
                this.state.loading = false;
                return;
            }
            
            this.state.qrCode = result.qr_code;
            this.state.paymentUri = result.payment_uri;
            this.state.loading = false;
            
            console.log('[Algorand][Popup] QR code generated successfully');
        } catch (error) {
            console.error('[Algorand][Popup] Error:', error);
            this.state.error = error.message || 'Failed to generate QR code';
            this.state.loading = false;
        }
    }
    
    confirm() {
        // User confirms they've paid
        this.props.close({ confirmed: true });
    }
    
    cancel() {
        this.props.close({ confirmed: false });
    }
}

