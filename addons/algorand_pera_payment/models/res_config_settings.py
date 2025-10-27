# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    algorand_merchant_address = fields.Char(string="Algorand Merchant Address")
    algorand_algod_url = fields.Char(
        string="Algod URL", default="https://testnet-api.algonode.cloud"
    )
    algorand_algod_token = fields.Char(string="Algod Token")

    def set_values(self):
        super().set_values()
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param("algorand.merchant_address", self.algorand_merchant_address or "")
        icp.set_param("algorand.algod_url", self.algorand_algod_url or "")
        icp.set_param("algorand.algod_token", self.algorand_algod_token or "")

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env["ir.config_parameter"].sudo()
        res.update(
            algorand_merchant_address=icp.get_param("algorand.merchant_address") or "",
            algorand_algod_url=icp.get_param("algorand.algod_url")
            or "https://testnet-api.algonode.cloud",
            algorand_algod_token=icp.get_param("algorand.algod_token") or "",
        )
        return res
