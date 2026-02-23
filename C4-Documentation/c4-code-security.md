# C4 Code Level: security

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Access Rights |
| **Description** | CSV access rules for public read on payment provider, transaction, and method. |
| **Location** | [addons/algorand_pera_payment/security/ir.model.access.csv](../addons/algorand_pera_payment/security/ir.model.access.csv) |
| **Language** | CSV (Odoo ir.model.access) |
| **Purpose** | Allow `base.group_public` to read (only) payment provider, payment transaction, and payment method so checkout can display and process Algorand payments. |

## Code Elements

| id | name | model_id:id | group_id:id | perm_read | perm_write | perm_create | perm_unlink |
|----|------|-------------|-------------|-----------|------------|-------------|-------------|
| access_payment_provider_algorand_pera_public | payment.provider.algorand_pera.public | payment.model_payment_provider | base.group_public | 1 | 0 | 0 | 0 |
| access_payment_transaction_algorand_pera_public | payment.transaction.algorand_pera.public | payment.model_payment_transaction | base.group_public | 1 | 0 | 0 | 0 |
| access_payment_method_algorand_pera_public | payment.method.algorand_pera.public | payment.model_payment_method | base.group_public | 1 | 0 | 0 | 0 |

## Dependencies

- **Internal**: Loaded by `__manifest__.py` first in `data` list.
- **External**: Odoo security (ir.model.access), base.group_public, payment module models.

## Relationships

- Grants: Public users read access to payment.provider, payment.transaction, payment.method.
- Required for: Checkout form (read provider/transaction/method), controller sudo browse.
