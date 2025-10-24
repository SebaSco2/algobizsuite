# Copyright 2025 Odoo Community Association (OCA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# The codes of the payment methods to activate when Algorand Pera Wallet is activated.
DEFAULT_PAYMENT_METHOD_CODES = {
    'algorand_pera',
}

# Mapping of payment method codes to Algorand codes.
PAYMENT_METHODS_MAPPING = {
    'algorand_pera': 'algorand_pera',
}

# Common Algorand Standard Asset (ASA) constants used by the module.
# Note: IDs are well-known public ASAs for USDC on Algorand.
# - MainNet USDC (Circle): 31566704
# - TestNet USDC: 10458941
USDC_ASA_IDS_BY_NETWORK = {
    'mainnet': 31566704,
    'testnet': 10458941,
}

# Number of fractional decimals for USDC on Algorand
USDC_DECIMALS = 6
