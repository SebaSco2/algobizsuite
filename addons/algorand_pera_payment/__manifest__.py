{
    "name": "Payment - Algorand (Pera Wallet)",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/payment",
    "category": "Accounting/Payment",
    "development_status": "Beta",
    "summary": "Add Pera Wallet (Algorand) payment option to website checkout and Point of Sale",
    "depends": ["website_sale", "payment", "point_of_sale"],
    "external_dependencies": {
        "python": ["algosdk", "qrcode"]
    },
    "images": ["static/description/icon.png"],
    "data": [
        "security/ir.model.access.csv",
        "views/payment_form.xml",
        "views/payment_method_views.xml",
        "views/payment_provider_views.xml",
        "views/pos_payment_method_views.xml",
        "views/shop_confirmation.xml",
        "data/payment_provider_data.xml",
        "data/payment_method_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "algorand_pera_payment/static/src/js/**/*",
            "algorand_pera_payment/static/src/css/**/*",
        ],
        "point_of_sale._assets_pos": [
            "algorand_pera_payment/static/src/app/*.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}

