# C4 Code Level: controllers

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment HTTP Controllers |
| **Description** | HTTP and JSON routes for payment form display and payment processing. |
| **Location** | [addons/algorand_pera_payment/controllers/](../addons/algorand_pera_payment/controllers/) |
| **Language** | Python |
| **Purpose** | Serve the Algorand payment form and process blockchain confirmation callbacks from the frontend. |

## Code Elements

### main.py

| Element | Type | Description | Location |
|---------|------|-------------|----------|
| `PeraPaymentController` | Class | `http.Controller` for Algorand Pera routes. | main.py:11-12 |
| `algorand_pera_form(self, **kwargs)` | Method | **Route**: `GET/POST /payment/algorand_pera/form`, auth=public, csrf=False. Renders payment form: validates `tx_id` and `reference`, loads `payment.transaction` and provider, returns `algorand_pera_payment.payment_form` template with tx, provider, merchant_address, amount, currency, order_id. Redirects to `/shop` if invalid. | 14-59 |
| `algorand_pera_process(self, **kwargs)` | Method | **Route**: `POST /payment/algorand_pera/process`, type=json, auth=public, csrf=False. Processes payment after blockchain confirmation. Expects `tx_id`, `tx_hash`, `sender_address`, `error_message`. On error returns JSON `{error, message, type}`. Loads transaction, calls `tx._process("algorand_pera", data)`, registers with `PaymentPostProcessing.monitor_transaction(tx)`, confirms sale order if `sale_order_id` in session, returns `{success: True, tx_id: tx_hash}`. | 61-202 |

### Function signatures (summary)

- `algorand_pera_form(self, **kwargs)` → HTTP response (redirect or rendered template).
- `algorand_pera_process(self, **kwargs)` → dict (`{success, tx_id}` or `{error, message, type}`).

## Dependencies

- **Internal**: `request`, `payment.transaction`, `sale.order`, `odoo.addons.payment.controllers.post_processing.PaymentPostProcessing`.
- **External**: `odoo.http`, `request.render`, `request.redirect`, `request.env`, `request.session`.

## Relationships

- Called by: Frontend (browser) – form page load and JSON RPC after wallet signs transaction.
- Uses: `payment.transaction`, `payment.provider`, `sale.order`, `PaymentPostProcessing.monitor_transaction`.
