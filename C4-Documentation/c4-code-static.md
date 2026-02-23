# C4 Code Level: static

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Frontend Assets |
| **Description** | JavaScript (OWL/patch), CSS, images, and third-party libs for checkout payment form and Pera Wallet. |
| **Location** | [addons/algorand_pera_payment/static/](../addons/algorand_pera_payment/static/) |
| **Language** | JavaScript (OWL), CSS |
| **Purpose** | Render inline payment form, connect Pera Wallet, build/sign/broadcast Algorand transactions, and call backend process route. |

## Code Elements

### static/src/js/payment_form.js

| Element | Type | Description |
|---------|------|-------------|
| Patch target | `PaymentForm` from `@payment/interactions/payment_form` | OWL patch. |
| `setup()` | Method | Calls super, sets `this.algorandElements = {}`. |
| `_initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow)` | Method | For `algorand_pera`: checks wallet connected, merchant address, USDC opt-in; then calls `super._initiatePaymentFlow`. |
| `_processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues)` | Method | For `algorand_pera` calls `_processAlgorandPayment(processingValues)`; on error shows dialog. |
| `_getAlgorandFormValues()` | Method | Reads inline form values from DOM (`o_algorand_element_container` data attribute). |
| `_processAlgorandPayment(processingValues)` | Method | Builds transaction (ALGO or ASA), signs with Pera Wallet, broadcasts, calls `/payment/algorand_pera/process` with tx_id, tx_hash, sender_address; handles redirect/status. |
| (Other helpers) | Various | Wallet connect/disconnect, ASA opt-in check, transaction building (algosdk), error display. |

### static/src/app/algorand_payment_popup.js

| Element | Type | Description |
|---------|------|-------------|
| `AlgorandPaymentPopup` | OWL Component | Template `algorand_pera_payment.AlgorandPaymentPopup`. |
| `setup()` | Method | Uses rpc service, state: qrCode, loading, error, paymentUri; calls `generateQRCode()`. |
| `generateQRCode()` | Method | RPC `/pos/algorand/qr_code` with payment_method_id, amount, currency_id, order_ref; sets qrCode, paymentUri, loading, error. |
| `confirm()` / `cancel()` | Method | Close popup with confirmed true/false. |

### static/src/css/payment_form.css

- Styles for `.algorand-payment-container` and payment form layout (buttons, QR, wallet connect).

### static/src/images/

- `pera_logo.svg`, `algorand_logo_mark_black.svg` – logos for UI.

### static/src/lib/

- `pera-wallet-connect.umd.js` – Pera Wallet connect SDK.
- `algosdk.min.js` – Algorand SDK (transactions, encoding).

## Dependencies

- **Internal**: Odoo assets `web.assets_frontend`; template `algorand_pera_payment.payment_form`; backend route `/payment/algorand_pera/process`.
- **External**: `@payment/interactions/payment_form`, `@web/core/l10n/translation`, `@web/core/utils/patch`, Pera Wallet Connect, algosdk (browser).

## Relationships

- Consumes: Inline form values from QWeb (`o_algorand_element_container`), provider/transaction from backend.
- Calls: `/payment/algorand_pera/process` (JSON), Pera Wallet (sign/broadcast), Algorand node (broadcast).
- Used by: Website checkout payment step (payment form).
