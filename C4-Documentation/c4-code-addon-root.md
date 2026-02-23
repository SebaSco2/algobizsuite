# C4 Code Level: addon root

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Addon Root |
| **Description** | Module entry point and manifest (metadata, dependencies, data, assets, hooks). |
| **Location** | [addons/algorand_pera_payment/](../addons/algorand_pera_payment/) (__init__.py, __manifest__.py) |
| **Language** | Python |
| **Purpose** | Define module identity, depend on website_sale and payment, load subpackages and post_init_hook, register data and frontend assets. |

## Code Elements

### __init__.py

- Imports: `controllers`, `models`, `post_init_hook` from `.hooks`.
- Purpose: Load controllers and models; expose `post_init_hook` for manifest.

### __manifest__.py

| Key | Value |
|-----|--------|
| name | "Payment - Algorand (Pera Wallet)" |
| version | "19.0.1.0.0" |
| license | "AGPL-3" |
| category | "Accounting/Payment" |
| depends | ["website_sale", "payment"] |
| external_dependencies | {"python": ["algosdk"]} |
| data | security, views, data XML (order matters) |
| assets | web.assets_frontend: payment_form.js, payment_form.css |
| post_init_hook | "post_init_hook" |
| installable | True, auto_install False |

## Dependencies

- **Internal**: controllers, models, hooks.post_init_hook.
- **External**: Odoo addon loader, website_sale, payment, algosdk (Python).

## Relationships

- Loads: controllers, models; registers hook.
- Used by: Odoo to load and install the addon.
