Customer Experience
==================

When a customer selects Algorand Pera Wallet as their payment method:

1. The payment form displays the payment details (amount, merchant address)
2. Customer clicks "Connect Wallet" to connect their Pera Wallet
3. Pera Wallet prompts the customer to approve the connection
4. Once connected, the customer's wallet address is displayed
5. For USDC payments, the system automatically checks if the customer needs to opt-in to USDC
6. Customer clicks "Pay Now"
7. Pera Wallet prompts the customer to sign and approve the transaction
8. Transaction is broadcast to the Algorand blockchain
9. Payment is confirmed within seconds (typically under 5 seconds)
10. Customer is redirected to /payment/status page showing payment confirmation
11. Order is automatically confirmed and customer receives order confirmation
12. Cart is automatically cleared when customer navigates to shop

Payment Flow Architecture
=========================

The payment process follows Odoo's standard payment provider flow:

**Frontend (Customer Side)**:
1. **Transaction Initialization**: Customer selects Algorand payment method
2. **Wallet Connection**: Pera Wallet SDK connects to customer's wallet
3. **Transaction Building**: Module constructs Algorand transaction (payment or ASA transfer)
4. **Transaction Signing**: Customer signs transaction in Pera Wallet (private keys never leave wallet)
5. **Blockchain Broadcast**: Signed transaction is broadcast to Algorand network
6. **Backend Notification**: Frontend sends transaction hash to backend

**Backend (Server Side)**:
1. **Transaction Processing**: `_process()` method updates transaction state
2. **Transaction Monitoring**: `monitor_transaction()` registers tx for status page
3. **Order Confirmation**: Sale order is confirmed (state: draft → sale)
4. **Session Management**: Session is explicitly saved for status page
5. **Post-Processing**: Odoo's cron handles payment creation and invoice reconciliation

**Automatic Cart Clearing**:
- When order is confirmed (state != 'draft'), it's no longer a cart
- Customer navigates to /shop or /shop/cart
- website_sale controller detects order.state != 'draft'
- session['sale_order_id'] is automatically cleared
- Cart badge updates via page reload (no manual intervention needed)

Supported Payment Types
=======================

**ALGO Payments** (Native Cryptocurrency):
- Direct payments in Algorand's native token
- No asset opt-in required
- Supported for any currency configured to use ALGO
- Fastest option with minimal setup

**USDC Payments** (USD Stablecoin):
- Payments using Circle's USDC on Algorand
- Requires both merchant AND customer to be opted-in to USDC asset
- Automatic opt-in status verification
- Clear user prompts if opt-in is needed
- Supported for USD currency only

Transaction Verification
========================

All payments are cryptographically verified on the Algorand blockchain, ensuring:

* **Payment Authenticity**: Transaction signature verified by blockchain
* **Correct Amount**: Blockchain ensures exact amount was transferred
* **Correct Recipient**: Payment to merchant's configured address
* **Immutability**: Transaction cannot be reversed or modified
* **Fast Finality**: Confirmed in one block (~3.7 seconds)

Error Handling
==============

The module provides comprehensive error handling:

**Pre-Payment Validation**:
- ✓ Wallet connection status
- ✓ Merchant address configuration
- ✓ USDC opt-in for USD payments (both merchant and customer)
- ✓ Sufficient balance in customer wallet

**Payment Processing Errors**:
- Insufficient funds → Clear message to add more funds
- Transaction broadcast failure → Retry option
- Network connectivity issues → User-friendly error messages
- Wallet connection lost → Reconnection prompt

**Post-Payment**:
- Session persistence for status page
- Automatic transaction monitoring
- Order confirmation with error recovery
- Failed payments marked as 'error' state

Admin Features
==============

**Payment Provider Configuration**:
- Merchant address validation (58 characters, valid format)
- Network selection (TestNet/MainNet)
- Node URL configuration with verification button
- USDC opt-in status checker
- Real-time blockchain verification

**Transaction Management**:
- Algorand transaction ID stored on payment.transaction
- Sender address tracking
- Network information (testnet/mainnet)
- Provider reference linked to blockchain transaction
- Full audit trail in transaction chatter

**Debugging Tools**:
- Comprehensive logging at all stages
- Transaction state tracking
- Frontend console logging for development
- Blockchain explorer links for transaction verification

Security Best Practices
=======================

**For Merchants**:
- ✓ Never share your wallet's private keys or recovery phrase
- ✓ Use the USDC opt-in checker to verify configuration
- ✓ Test thoroughly on TestNet before MainNet deployment
- ✓ Monitor incoming transactions regularly
- ✓ Keep secure backups of wallet recovery phrase
- ✓ Verify merchant address in configuration matches your wallet

**For Customers**:
- ✓ Always verify payment details before signing
- ✓ Check merchant address matches expected recipient
- ✓ Verify payment amount in Pera Wallet
- ✓ Keep Pera Wallet app updated
- ✓ Use secure device for transactions
