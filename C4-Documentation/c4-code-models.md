# C4 Code Level: models

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Models |
| **Description** | Odoo model extensions for payment provider, transaction, method, and settings. |
| **Location** | [addons/algorand_pera_payment/models/](../addons/algorand_pera_payment/models/) |
| **Language** | Python |
| **Purpose** | Extend Odoo payment and config models to support Algorand Pera Wallet (provider config, transaction state, method display, system settings). |

## Code Elements

### payment_provider.py

| Element | Type | Description | Location |
|---------|------|-------------|----------|
| `PaymentProvider` | Class | `_inherit = "payment.provider"`. Adds Algorand provider code and fields. | payment_provider.py:15-21 |
| `code` | Field | `Selection(selection_add=[("algorand_pera", "Algorand Pera Wallet")], ondelete={"algorand_pera": "set default"})` | 18-21 |
| `_algorand_effective_network()` | Method | Returns `"mainnet"` if `state == "enabled"` else `"testnet"`. | 24-31 |
| `algorand_merchant_address` | Field | Char – merchant Algorand address. | 33-36 |
| `_onchange_state_set_default_node()` | Method | `@api.onchange("state")` – sets `algorand_node_url` from network. | 38-49 |
| `algorand_network` | Field | Selection testnet/mainnet, default testnet. | 51-56 |
| `algorand_node_url` | Field | Char – Algorand node URL. | 58-62 |
| `image_128` | Field | Image – provider logo. | 65-70 |
| `_get_supported_currencies()` | Method | For `algorand_pera` returns USD only. | 75-81 |
| `_get_supported_flows()` | Method | For `algorand_pera` returns `["direct"]`. | 83-87 |
| `_get_default_payment_method_codes()` | Method | For `algorand_pera` returns `const.DEFAULT_PAYMENT_METHOD_CODES`. | 89-95 |
| `_algorand_get_inline_form_values(...)` | Method | Returns JSON of inline form values (tx_id, merchant_address, amount, currency, network, node_url, is_asa, asset_id, etc.). | 96-179 |
| `_send_payment_request(tx_sudo)` | Method | For Algorand sets transaction state to pending; no external HTTP request. | 181-189 |
| `_check_algorand_merchant_address()` | Method | `@api.constrains` – validates merchant address present and 58 chars when enabled/test. | 193-220 |
| `_check_algorand_usdc_optin()` | Method | Uses algosdk to check if merchant address is opted-in to USDC ASA. | 222-281 |
| `action_algorand_verify_node()` | Method | Action – verifies node URL via algod client, returns notification. | 285-311 |
| `action_algorand_check_usdc_optin()` | Method | Action – checks USDC opt-in and shows notification. | 313-358 |
| `action_toggle_is_published()` | Method | Toggles `is_published` and reloads client. | 360-367 |

### payment_transaction.py

| Element | Type | Description | Location |
|---------|------|-------------|----------|
| `PaymentTransaction` | Class | `_inherit = "payment.transaction"`. | 11-12 |
| `algorand_tx_id` | Field | Char – Algorand transaction ID. | 14-17 |
| `algorand_sender_address` | Field | Char – sender address. | 19-22 |
| `algorand_network` | Field | Selection testnet/mainnet. | 24-31 |
| `_get_specific_processing_values(processing_values)` | Method | Returns Algorand processing values for inline form. | 33-52 |
| `_extract_amount_data(payment_data)` | Method | For Algorand returns amount/currency from transaction. | 57-70 |
| `_apply_updates(payment_data)` | Method | Sets provider_reference, algorand_tx_id, algorand_sender_address; calls `_set_done()`. | 72-124 |
| `_search_by_reference(provider_code, payment_data)` | Method | Finds transaction by `reference` and `provider_code='algorand_pera'`. | 126-148 |
| `_process_notification_data(provider_code, notification_data)` | Method | Writes tx_id, sender_address, state done/error. | 150-171 |
| `_get_tx_from_notification_data(provider_code, notification_data)` | Method | Finds transaction by reference. | 173-190 |
| `_execute_callback()` | Method | Delegates to super for Algorand. | 192-198 |

### payment_method.py

| Element | Type | Description | Location |
|---------|------|-------------|----------|
| `PaymentMethod` | Class | `_inherit = "payment.method"`. | 7-8 |
| `image` | Field | Image 64x64. | 9-14 |
| `image_payment_form` | Field | Related resized image for payment form. | 16-22 |

### res_config_settings.py

| Element | Type | Description | Location |
|---------|------|-------------|----------|
| `ResConfigSettings` | Class | `_inherit = "res.config.settings"`. | 7-8 |
| `algorand_merchant_address` | Field | Char – stored in `ir.config_parameter`. | 10 |
| `algorand_algod_url` | Field | Char – default testnet algod URL. | 11-13 |
| `algorand_algod_token` | Field | Char. | 14 |
| `set_values()` | Method | Persists params to `ir.config_parameter`. | 16-21 |
| `get_values()` | Method | Loads params from `ir.config_parameter`. | 23-32 |

## Dependencies

- **Internal**: `..const` (payment_provider).
- **External**: `odoo`, `odoo.exceptions.ValidationError`, `algosdk.v2client.algod` (optional), `payment.provider`, `payment.transaction`, `payment.method`, `res.config.settings`, `res.currency`, `ir.config_parameter`.

## Relationships

- Models extend: `payment.provider`, `payment.transaction`, `payment.method`, `res.config.settings`.
- Used by: controllers (main), views (QWeb inline form values), hooks.
