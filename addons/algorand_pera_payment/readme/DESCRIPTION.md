This module adds support for Algorand blockchain payments through Pera Wallet to Odoo's e-commerce platform.

Pera Wallet is a secure, open-source, non-custodial wallet for the Algorand blockchain that allows users to manage their Algorand (ALGO) assets and Algorand Standard Assets (ASAs) like USDC.

Key Features:
* Accept payments in ALGO (Algorand's native cryptocurrency)
* Accept payments in USDC (via Algorand Standard Assets)
* Direct wallet-to-wallet transactions without intermediaries
* Low transaction fees (typically less than $0.01)
* Fast confirmation times (under 5 seconds)
* Secure blockchain-based payment verification
* Automatic order confirmation upon payment
* Seamless integration with Odoo's e-commerce workflow

Technical Highlights:
* Follows Odoo's standard payment provider patterns
* Automatic cart clearing after successful payment
* Transaction monitoring on /payment/status page
* Built-in USDC opt-in verification for both merchant and customer
* Comprehensive error handling and user feedback
* OCA compliant module structure

Why Algorand?
* Low fees: Transaction costs are typically under $0.01
* Fast: Block times of ~3.7 seconds for near-instant confirmation
* Scalable: Handles 6,000+ transactions per second
* Eco-friendly: Carbon-negative blockchain
* Secure: Pure proof-of-stake consensus with strong finality guarantees
