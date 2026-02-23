# C4 Code Level: views

## Overview

| Attribute | Value |
|-----------|--------|
| **Name** | Algorand Pera Payment Views |
| **Description** | QWeb templates and backend view definitions (XML) for payment form, provider, method, and shop confirmation. |
| **Location** | [addons/algorand_pera_payment/views/](../addons/algorand_pera_payment/views/) |
| **Language** | XML (Odoo QWeb / view definitions) |
| **Purpose** | Define payment form template with inline Algorand values, provider/method admin views, and shop confirmation content. |

## Code Elements

### payment_form.xml

| Element | Type | Description |
|---------|------|-------------|
| `algorand_inline_form` | Template | Sets `inline_form_values` via `provider_sudo._algorand_get_inline_form_values(amount, currency, partner_id, mode == 'validation', payment_method_sudo=pm_sudo, sale_order_id=sale_order_id)`. Renders div `name="o_algorand_element_container"` with `t-att-data-algorand-inline-form-values="inline_form_values"` and class `algorand-payment-container`. Frontend JS reads this data. |

### payment_provider_views.xml

- Form and list views for `payment.provider`: Algorand merchant address, network, node URL, logo, actions “Verify Node” and “Check USDC Opt-in”, publish toggle.

### payment_method_views.xml

- Views for `payment.method`: image and payment form image fields.

### shop_confirmation.xml

- Template(s) for shop order confirmation (e.g. Algorand tx id / explorer link on confirmation page).

## Dependencies

- **Internal**: `provider_sudo._algorand_get_inline_form_values` (models), frontend JS reading `o_algorand_element_container`.
- **External**: Odoo view engine, `website_sale`, `payment` module templates.

## Relationships

- Used by: Controllers (render `payment_form`), frontend (inline form values), Odoo UI (provider/method views).
- Depends on: models (payment_provider for inline form values).
