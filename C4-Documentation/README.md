# C4 Architecture Documentation – AlgoBizSuite (Odoo 19 + Algorand Pera Payment)

This folder contains **C4 model** documentation for the Algorand Pera Payment Odoo addon and its runtime (AlgoBizSuite), produced in a bottom-up order: Code → Component → Container → Context.

## Reading Order

| Level | Document | Audience |
|-------|----------|----------|
| **Context** | [c4-context.md](c4-context.md) | Everyone: system purpose, users, external systems, high-level flows |
| **Container** | [c4-container.md](c4-container.md) | DevOps / deployment: Odoo 19, PostgreSQL, APIs |
| **Component** | [c4-component.md](c4-component.md) + [c4-component-*.md](c4-component-payment-provider.md) | Developers: logical components and their interfaces |
| **Code** | [c4-code-*.md](c4-code-models.md) | Developers: functions, classes, and file locations |

## Contents

```
C4-Documentation/
├── README.md                    # This file
├── c4-context.md                 # System context, personas, user journeys
├── c4-container.md               # Containers (Odoo 19, PostgreSQL)
├── c4-component.md               # Master component index
├── c4-component-payment-*.md     # Per-component docs (4 components)
├── c4-code-*.md                  # Per-area code-level docs (10 files)
└── apis/
    └── odoo19-payment-algorand-api.yaml   # OpenAPI 3.1 for payment routes
```

## Quick Links

- **What the system does**: [c4-context.md](c4-context.md#system-overview)
- **Who uses it**: [c4-context.md](c4-context.md#personas)
- **Customer payment flow**: [c4-context.md](c4-context.md#2-pay-with-algorand--customer-journey)
- **Containers and deployment**: [c4-container.md](c4-container.md)
- **Payment HTTP API**: [apis/odoo19-payment-algorand-api.yaml](apis/odoo19-payment-algorand-api.yaml)
