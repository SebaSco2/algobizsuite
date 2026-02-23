# C4 Code Level: hooks

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Post-Init Hook |
| **Description** | Post-install hook to create/link payment methods and account payment method lines. |
| **Location** | [addons/algorand_pera_payment/hooks.py](../addons/algorand_pera_payment/hooks.py) |
| **Language** | Python |
| **Purpose** | Ensure default payment methods exist for the provider and journal payment method lines are linked after module install. |

## Code Elements

### Functions

| Function | Signature | Description | Location |
|----------|-----------|-------------|----------|
| `post_init_hook` | `post_init_hook(env)` | Post-install hook. Finds `payment.provider` with `code='algorand_pera'`, ensures default payment methods are in `provider.payment_method_ids`, and creates `account.payment.method.line` for provider journal if missing. | hooks.py:5-43 |

**Parameters**

- `env`: Odoo environment (from `odoo.api.Environment`).

**Dependencies**: `payment.provider`, `payment.method`, `account.payment.method`, `account.payment.method.line`.

## Dependencies

- **Internal**: Referenced by `__init__.py` as `post_init_hook`; declared in `__manifest__.py` as `post_init_hook`.
- **External**: Odoo ORM (`env`), standard Odoo models `payment.provider`, `payment.method`, `account.payment.method`, `account.payment.method.line`.

## Relationships

- Invoked by: Odoo at module install (via `__manifest__.py` `post_init_hook`).
- Uses: `payment.provider`, `payment.method`, `account.payment.method`, `account.payment.method.line`.
