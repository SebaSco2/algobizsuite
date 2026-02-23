# C4 Code Level: data

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Data |
| **Description** | XML data files that create default payment provider and payment method records. |
| **Location** | [addons/algorand_pera_payment/data/](../addons/algorand_pera_payment/data/) |
| **Language** | XML (Odoo data) |
| **Purpose** | Load initial payment provider and payment method so “Algorand Pera Wallet” is available in Odoo. |

## Code Elements

### payment_provider_data.xml

- Declares default `payment.provider` record: code `algorand_pera`, name “Algorand Pera Wallet”, state/test/enabled, journal and branding as needed.

### payment_method_data.xml

- Declares default `payment.method` record: code `algorand_pera`, name “Algorand (Pera Wallet)”, linked to provider.

## Dependencies

- **Internal**: Loaded by `__manifest__.py` `data` list.
- **External**: Odoo data loading, `payment.provider`, `payment.method` models.

## Relationships

- Used by: Odoo on module install/update.
- Creates: `payment.provider` (algorand_pera), `payment.method` (algorand_pera).
