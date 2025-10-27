# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentMethod(models.Model):
    _inherit = "payment.method"

    image = fields.Image(
        string="Image",
        help="The base image used for this payment method; in a 64x64 px format.",
        max_width=64,
        max_height=64,
    )

    image_payment_form = fields.Image(
        string="The resized image displayed on the payment form.",
        related="image",
        store=True,
        max_width=45,
        max_height=30,
    )
