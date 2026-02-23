# C4 Code Level: const

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Constants |
| **Description** | Module-wide constants for payment method codes, USDC ASA IDs, and decimals. |
| **Location** | [addons/algorand_pera_payment/const.py](../addons/algorand_pera_payment/const.py) |
| **Language** | Python |
| **Purpose** | Centralize Algorand-specific configuration (payment method codes, USDC asset IDs per network, decimals). |

## Code Elements

### Module-level constants

| Name | Type | Description |
|------|------|-------------|
| `DEFAULT_PAYMENT_METHOD_CODES` | `set` | `{"algorand_pera"}` – payment method codes to activate when provider is activated. |
| `PAYMENT_METHODS_MAPPING` | `dict` | `{"algorand_pera": "algorand_pera"}` – mapping of payment method codes to Algorand codes. |
| `USDC_ASA_IDS_BY_NETWORK` | `dict` | `{"mainnet": 31566704, "testnet": 10458941}` – USDC ASA IDs per Algorand network. |
| `USDC_DECIMALS` | `int` | `6` – fractional decimals for USDC on Algorand. |

## Dependencies

- **Internal**: None (leaf module).
- **External**: None.

## Relationships

- Used by: `models/payment_provider.py` (`_get_default_payment_method_codes`, `_algorand_get_inline_form_values`, `_check_algorand_usdc_optin`, `action_algorand_check_usdc_optin`).
