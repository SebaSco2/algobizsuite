19.0.1.0.0 (2025-10-17)
=======================

**Initial Release - Production Ready**

Core Features:
--------------
* Support for ALGO payments via Pera Wallet
* Support for USDC payments (Algorand Standard Asset)
* Direct blockchain payment verification
* Automatic order confirmation upon payment
* TestNet and MainNet support
* Merchant address validation with blockchain verification
* USDC opt-in status checker for merchant and customer

Payment Flow:
-------------
* Follows Odoo's standard payment provider architecture
* Automatic cart clearing after successful payment
* Transaction monitoring on /payment/status page
* Session persistence for reliable redirects
* Comprehensive error handling and user feedback

Code Quality:
-------------
* Removed all external code references
* Added comprehensive inline documentation
* Followed Odoo's standard payment patterns
* OCA compliant module structure
* ~200 lines of zombie code removed for maintainability

Technical Implementation:
-------------------------
* Pera Wallet Connect SDK integration
* JSON-RPC API communication
* Automatic transaction state management
* Post-processing via Odoo's standard cron
* Race condition prevention through proper session handling

Security & Validation:
----------------------
* Merchant address format validation (58 characters)
* USDC opt-in verification for both parties
* Blockchain transaction verification
* Secure wallet connection via Pera Wallet
* No private key handling (non-custodial)

Admin Features:
---------------
* Network configuration (TestNet/MainNet)
* Node URL verification button
* USDC opt-in status checker
* Transaction tracking with blockchain IDs
* Comprehensive logging for debugging

Documentation:
--------------
* Complete installation guide
* Step-by-step configuration instructions
* Usage documentation with flow diagrams
* Security best practices
* OCA contribution guidelines compliant
