# C4 Code Level: migrations

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Migrations |
| **Description** | Version 19.0.1.0.0 migration to normalize payment method and provider names. |
| **Location** | [addons/algorand_pera_payment/migrations/19.0.1.0.0/](../addons/algorand_pera_payment/migrations/19.0.1.0.0/) |
| **Language** | Python (raw SQL / ORM via cr) |
| **Purpose** | Update existing payment_method and payment_provider records to canonical names and state. |

## Code Elements

### post-migration.py

| Element | Type | Description | Location |
|---------|------|-------------|----------|
| `migrate(cr, version)` | Function | Migration entry. Finds `payment_transaction` rows using old `payment_method` (code `algorand_pera`, name != 'Algorand (Pera Wallet)'). Updates `payment_method`: name to 'Algorand (Pera Wallet)', active true. Updates `payment_provider`: name 'Algorand Pera Wallet', state 'enabled', is_published true where code 'algorand_pera'. | post-migration.py:3-33 |

**Parameters**

- `cr`: Database cursor.
- `version`: Previous version string (unused in body).

## Dependencies

- **Internal**: None.
- **External**: Odoo migration framework, PostgreSQL (cr.execute).

## Relationships

- Invoked by: Odoo on module upgrade to 19.0.1.0.0.
- Modifies: `payment_method`, `payment_provider` tables.
