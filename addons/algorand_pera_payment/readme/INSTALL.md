Prerequisites
============

**Required Python Package**:
```bash
pip install algosdk
```

The `algosdk` package is required for Algorand blockchain interaction (transaction building, address validation, and blockchain verification).

**Required for Merchant**:
* An Algorand wallet address to receive payments
* Access to Pera Wallet (mobile app or web) to manage your merchant wallet

**Recommended for Testing**:
* A TestNet Algorand wallet
* TestNet ALGO from the faucet: https://bank.testnet.algorand.network/

Installation Steps
==================

1. **Install via Odoo Apps Menu**:
   - Navigate to **Apps**
   - Search for "Algorand Pera Payment"
   - Click **Install**

2. **Automatic Setup**:
   - The module automatically creates:
     - Payment provider record (Algorand Pera Wallet)
     - Payment method record (algorand_pera)
     - Account payment method (for journal integration)
   - Provider is created in **disabled** state by default

Post-Installation Configuration
================================

The provider **MUST** be configured before it can be enabled. Follow these steps:

Step 1: Basic Configuration
----------------------------

1. Go to **Website > Configuration > Payment Providers**
2. Select **Algorand Pera Wallet**
3. Configure required settings:

   **Merchant Algorand Address** (Required):
   - Your 58-character Algorand wallet address
   - Format: Uppercase letters and numbers (e.g., `ABC123...XYZ789`)
   - This is where you will receive payments
   - **Validation**: Module checks address format and length

   **Algorand Network**:
   - **TestNet**: For testing (default)
   - **MainNet**: For production

   **Algorand Node URL**:
   - TestNet: `https://testnet-api.algonode.cloud` (default)
   - MainNet: `https://mainnet-api.algonode.cloud`

Step 2: Verify Configuration
-----------------------------

Before enabling, verify your setup:

1. **Verify Node Connection**:
   - Click the **"Verify Node"** button
   - Confirms node URL is accessible
   - Checks Algorand network connectivity

2. **Check USDC Opt-in** (for USD payments):
   - Click **"Check USDC Opt-in Status"** button
   - Verifies if your merchant address is opted-in to USDC
   - Required for accepting USD payments
   - Optional for ALGO payments

Step 3: Enable Provider
------------------------

1. **Set State**:
   - Change **State** from "Disabled" to "Enabled" or "Test"
   - Module validates merchant address at this point
   - Validation errors will prevent enabling

2. **Publish Provider**:
   - Click the **"Published"** smart button in the header
   - Makes provider visible to customers
   - Provider must be enabled before publishing

Validation Rules
================

The module enforces strict validation:

**Hard Requirements** (Prevents Enabling):
- ❌ Merchant address must be configured
- ❌ Merchant address must be exactly 58 characters
- ❌ Merchant address must have valid format
- ❌ State cannot be 'enabled' or 'test' without valid merchant address

**Warnings** (Does Not Prevent Enabling):
- ⚠️ Merchant not opted-in to USDC → Cannot accept USD payments
- ⚠️ Still allows ALGO payments

Accepting Different Currencies
===============================

**ALGO Payments** (Always Available):
- No special configuration needed
- Works immediately after enabling provider
- Merchant address is all that's required

**USD/USDC Payments** (Requires Opt-in):
1. Your merchant address must be opted-in to USDC asset
2. Use **"Check USDC Opt-in Status"** button to verify
3. To opt-in:
   - Open Pera Wallet
   - Go to "Add Asset"
   - Search for "USDC"
   - Verify Asset ID:
     - MainNet: `31566704` (Circle USDC)
     - TestNet: `10458941` (Test USDC)
   - Complete opt-in transaction (requires small ALGO for fee)

4. After opt-in, click **"Check USDC Opt-in Status"** again to confirm

Testing Your Setup
==================

**Before Going Live**:

1. **Use TestNet First**:
   - Configure provider with TestNet settings
   - Use TestNet merchant address
   - Test full payment flow
   - Get free TestNet ALGO from faucet

2. **Test Payment Flow**:
   - Add product to cart
   - Go to checkout
   - Select Algorand Pera Wallet
   - Connect wallet
   - Complete test payment
   - Verify order confirmation
   - Check payment in Pera Wallet history

3. **Verify in Odoo**:
   - Check payment.transaction record
   - Verify Algorand transaction ID stored
   - Check sale order is confirmed
   - Verify account.payment created (if applicable)

4. **Switch to MainNet**:
   - Update Network to MainNet
   - Update Node URL to MainNet
   - Update Merchant Address to MainNet address
   - Re-verify USDC opt-in for MainNet
   - Test with small real payment first

Troubleshooting
===============

**Cannot Enable Provider**:
- Check merchant address is exactly 58 characters
- Verify address format (no spaces, special characters)
- Check provider state transitions (disabled → test/enabled)

**USDC Payments Not Working**:
- Verify merchant opted-in using "Check USDC Opt-in Status"
- Verify correct Asset ID for your network (TestNet vs MainNet)
- Check customer also has USDC opt-in

**Node Connection Fails**:
- Verify Node URL is correct
- Check internet connectivity
- Try alternative node URLs:
  - AlgoNode: `https://testnet-api.algonode.cloud`
  - PureStake: `https://testnet-algorand.api.purestake.io/ps2`

**Module Installation Issues**:
- Verify `algosdk` package is installed
- Check Python version compatibility (3.8+)
- Review Odoo logs for errors
