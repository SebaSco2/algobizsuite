/** @odoo-module **/
/* global algosdk */
console.info('[Algorand][frontend] payment_form.js loaded');

import { _t } from '@web/core/l10n/translation';
import { patch } from '@web/core/utils/patch';

import { PaymentForm } from '@payment/interactions/payment_form';


patch(PaymentForm.prototype, {

    setup() {
        super.setup();
        this.algorandElements = {}; // Store the element of each instantiated payment method.
        
    },

    // Remove submitForm override - let the standard flow handle it

    /**
     * Override payment flow initiation to handle Algorand-specific validations.
     * 
     * Before initiating payment, we check:
     * - Wallet is connected
     * - Merchant address is configured
     * - For USDC payments: both sender and merchant are opted-in to the USDC asset
     */
    async _initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow) {
        console.info('[Algorand][frontend] _initiatePaymentFlow', { providerCode, paymentOptionId, paymentMethodCode, flow });
        if (providerCode !== 'algorand_pera') {
            await super._initiatePaymentFlow(...arguments);
            return;
        }

        // For Algorand, check if wallet is connected
        const connectedAddress = document.querySelector('#connected-address');
        if (!connectedAddress || !connectedAddress.textContent) {
            // Show error if wallet not connected
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-warning mt-2';
            errorDiv.innerHTML = `
                <strong>Wallet Not Connected:</strong> Please connect your Pera Wallet first before proceeding with payment.
            `;
            
            const container = document.querySelector('[name="o_algorand_element_container"]') || document.body;
            container.appendChild(errorDiv);
            
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 5000);
            return;
        }

        // Check ASA opt-in if required
        const values = this._getAlgorandFormValues();
        if (!values.merchant_address) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-2';
            errorDiv.innerHTML = `
                <strong>Payment Failed:</strong> Merchant address is not configured. Please contact support.
            `;
            const container = document.querySelector('[name="o_algorand_element_container"]') || document.body;
            container.appendChild(errorDiv);
            setTimeout(() => { if (errorDiv.parentNode) errorDiv.parentNode.removeChild(errorDiv); }, 8000);
            return;
        }
        
        const container = document.querySelector('[name="o_algorand_element_container"]');
        const isAsa = Boolean(values && values.is_asa && values.asset_id);
        const optedIn = container ? container.dataset.asaOptedIn === 'true' : false;
        const merchantOpted = container ? container.dataset.merchantAsaOptedIn === 'true' : true;
        if (isAsa && (!optedIn || !merchantOpted)) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-warning mt-2';
            errorDiv.innerHTML = `
                <strong>USDC Not Ready:</strong> ${!optedIn ? `Please opt-in to ${values.currency_display_name || 'USDC'} in your wallet.` : ''} ${!merchantOpted ? `Merchant is not opted-in to ${values.currency_display_name || 'USDC'}.` : ''}
            `;
            const host = container || document.body;
            host.appendChild(errorDiv);
            setTimeout(() => { if (errorDiv.parentNode) errorDiv.parentNode.removeChild(errorDiv); }, 5000);
            const asaStatus = document.querySelector('#asa-status');
            if (asaStatus) asaStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        // Call parent to create the transaction in Odoo
        await super._initiatePaymentFlow(...arguments);
    },

    /**
     * Process Algorand payment using Pera Wallet.
     * 
     * This is the main payment flow:
     * 1. Build Algorand transaction (payment or ASA transfer)
     * 2. Sign transaction with Pera Wallet
     * 3. Broadcast to Algorand network
     * 4. Notify backend with transaction ID
     * 5. Redirect to /payment/status page
     */
    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'algorand_pera') {
            await super._processDirectFlow(...arguments);
            return;
        }

        console.info('[Algorand][frontend] _processDirectFlow called with processingValues:', processingValues);
        
        // Process the Algorand payment with the created transaction
        try {
            await this._processAlgorandPayment(processingValues);
        } catch (error) {
            console.error('[Algorand][frontend] Error in _processAlgorandPayment:', error);
            this._displayErrorDialog(_t("Payment processing failed"), error.message);
            this._enableButton();
        }
    },

    /**
     * Process Algorand payment using Pera Wallet
     */
    async _processAlgorandPayment(processingValues = null) {
        console.info('[Algorand][frontend] _processAlgorandPayment entered with processingValues:', processingValues);
        const connectedAddress = document.querySelector('#connected-address');
        const connectedAddressValue = connectedAddress.textContent;
        console.info('[Algorand][frontend] connectedAddress length', (connectedAddressValue || '').trim().length);
        
        // Get payment values from the form
        const values = this._getAlgorandFormValues();
        console.info('[Algorand][frontend] inline values snapshot', {
            hasValues: !!values,
            amount: values && values.amount,
            currency: values && (values.currency_display_name || values.currency_name),
            merchantLen: values && (values.merchant_address || '').length,
            network: values && values.network,
            isASA: !!(values && values.is_asa),
            tx_id: processingValues && processingValues.tx_id
        });
        if (!values || !values.merchant_address) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-2';
            errorDiv.innerHTML = `
                <strong>Payment Failed:</strong> Merchant address is not configured. Please contact support.
            `;
            const container = document.querySelector('[name="o_algorand_element_container"]') || document.body;
            container.appendChild(errorDiv);
            setTimeout(() => { if (errorDiv.parentNode) errorDiv.parentNode.removeChild(errorDiv); }, 8000);
            return;
        }
        
        try {
            // Load Algorand SDK
            console.info('[Algorand][frontend] loading algosdk');
            const algosdk = await (async function loadAlgorandSdkWithTimeout() {
                const timeoutMs = 7000;
                let timeoutId;
                const t = new Promise((_, rej) => {
                    timeoutId = setTimeout(() => rej(new Error('algosdk import timeout')), timeoutMs);
                });
                try {
                    const mod = await Promise.race([
                        import('https://esm.sh/algosdk@3.5.2'),
                        t,
                    ]);
                    clearTimeout(timeoutId);
                    console.info('[Algorand][frontend] algosdk loaded');
                    return mod;
                } catch (e) {
                    console.error('[Algorand][frontend] algosdk failed to load', e);
                    throw e;
                }
            })();
            
            const algodClient = new algosdk.Algodv2('', values.node_url, '');
            const params = await algodClient.getTransactionParams().do();
            console.info('[Algorand][frontend] fetched suggested params');
            console.debug('[Algorand][frontend] raw params', params);
            
            // Build algosdk v3 SuggestedParams (expects firstValid/lastValid keys)
            const minFee = Number(params.minFee ?? params.fee ?? 1000);
            const suggestedParams = {
                fee: Math.max(1000, minFee),
                flatFee: true,
                firstValid: Number(params.firstValid ?? params["first-round"] ?? params.firstRound),
                lastValid: Number(params.lastValid ?? params["last-round"] ?? params.lastRound),
                genesisID: params.genesisID,
                genesisHash: params.genesisHash,
            };
            console.debug('[Algorand][frontend] suggestedParams (firstValid/lastValid)', suggestedParams);

            const senderAddress = (connectedAddressValue || '').trim();
            const receiverAddress = (values.merchant_address || '').trim();
            console.info('[Algorand][frontend] addresses pre-validate', { senderLen: senderAddress.length, receiverLen: receiverAddress.length });
            console.info(`[Algorand][frontend] addresses pre-validate flat senderLen=${senderAddress.length} receiverLen=${receiverAddress.length}`);
            if (!senderAddress) {
                throw new Error('Connected wallet address is missing. Please reconnect your wallet.');
            }
            if (!receiverAddress) {
                throw new Error('Merchant address is missing. Please contact support.');
            }
            // Validate addresses strictly (reuse loaded algosdk module)
            if (!algosdk.isValidAddress(senderAddress)) {
                throw new Error('Connected wallet address is invalid. Please reconnect your wallet.');
            }
            if (!algosdk.isValidAddress(receiverAddress)) {
                throw new Error('Merchant address appears invalid. Please contact support.');
            }
            console.debug('[Algorand][frontend] txn inputs', {
                isASA: !!(values.is_asa && values.asset_id),
                assetId: values.asset_id,
                assetDecimals: values.asset_decimals,
                amount: values.amount,
                senderAddress,
                receiverAddress,
                network: values.network
            });

            // Build transaction note with host, amount, ASA, and order-payment relation
            const txNote = {
                host: window.location.host,
                amount: values.amount,
                currency: values.currency_display_name || values.currency_name,
                tx_id: (processingValues && processingValues.tx_id) || (values && values.tx_id) || null,
            };
            if (values.is_asa && values.asset_id) {
                txNote.asa_id = values.asset_id;
                txNote.asa_name = values.currency_display_name || values.currency_name;
            }
            const noteString = JSON.stringify(txNote);
            const noteBytes = new TextEncoder().encode(noteString);
            console.info('[Algorand][frontend] transaction note:', noteString);

            let transaction;
            try {
                if (values.is_asa && values.asset_id) {
                    console.info('[Algorand][frontend] building ASA transfer');
                    const asaAmount = Math.round(parseFloat(values.amount) * Math.pow(10, Number(values.asset_decimals || 6)));
                    const asaObject = {
                        sender: senderAddress,
                        receiver: receiverAddress,
                        amount: asaAmount,
                        assetIndex: Number(values.asset_id),
                        note: noteBytes,
                        suggestedParams,
                    };
                    console.debug('[Algorand][frontend] asaObject (sender/receiver keys)', asaObject);
                    transaction = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject(asaObject);
                } else {
                    console.info('[Algorand][frontend] building ALGO payment');
                    const payObject = {
                        sender: senderAddress,
                        receiver: receiverAddress,
                        amount: algosdk.algosToMicroalgos(parseFloat(values.amount)),
                        note: noteBytes,
                        suggestedParams,
                    };
                    console.debug('[Algorand][frontend] payObject', payObject);
                    transaction = algosdk.makePaymentTxnWithSuggestedParamsFromObject(payObject);
                }
            } catch (txBuildErr) {
                console.error('[Algorand][frontend] transaction build failed', txBuildErr);
                throw txBuildErr;
            }
            console.debug('[Algorand][frontend] built txn', transaction ? transaction.get_obj_for_encoding ? transaction.get_obj_for_encoding() : transaction : null);
            
            // Load Pera Wallet Connect (use existing instance if available)
            console.info('[Algorand][frontend] loading PeraWalletConnect');
            const PeraWalletConnect = await (async () => {
                try {
                    if (window.PeraWalletConnect) return window.PeraWalletConnect;
                    // Use ESM bundle from jsDelivr (no artificial timeouts or retries)
                    const mod = await import('https://cdn.jsdelivr.net/npm/@perawallet/connect@1.4.2/dist/pera-wallet-connect.mjs');
                    const P = mod.PeraWalletConnect || mod.default;
                    if (!P) throw new Error('PeraWalletConnect export missing');
                    window.PeraWalletConnect = P;
                    console.info('[Algorand][frontend] PeraWalletConnect loaded');
                    return P;
                } catch (e) {
                    console.error('[Algorand][frontend] Pera SDK failed to load', e);
                    throw e;
                }
            })();
            let peraWallet = window.peraWalletInstance;
            if (!peraWallet) {
                const chainId = (values.network === 'mainnet') ? 416001 : 416002;
                peraWallet = new PeraWalletConnect({ chainId });
                window.peraWalletInstance = peraWallet;
            }
            
            // Sign as a nested array group expected by Pera: [[{ txn }]]
            const txnGroup = [[{ txn: transaction }]];
            console.debug('[Algorand][frontend] signing group (nested)', txnGroup[0].map(t => t.txn && t.txn.get_obj_for_encoding ? t.txn.get_obj_for_encoding() : t));
            console.info('[Algorand][frontend] calling peraWallet.signTransaction');
            const signed = await peraWallet.signTransaction(txnGroup);
            // Flatten signed bytes to a simple array
            let signedBytes;
            if (Array.isArray(signed)) {
                signedBytes = Array.isArray(signed[0]) ? signed[0] : signed;
            } else if (signed && signed.byteLength !== undefined) {
                signedBytes = [signed];
            } else {
                signedBytes = [];
            }
            console.debug('[Algorand][frontend] signedBytes count', Array.isArray(signedBytes) ? signedBytes.length : 'n/a');
            if (!signedBytes.length) {
                throw new Error('No signed bytes returned by Pera');
            }

            // Broadcast transaction with flat bytes array
            console.info('[Algorand][frontend] broadcasting transaction');
            const sendResult = await algodClient.sendRawTransaction(signedBytes).do();
            console.debug('[Algorand][frontend] sendResult', sendResult);
            const txid = sendResult.txId || sendResult.txid;
            
            // Submit the payment to Odoo backend (best-effort)
            console.info('[Algorand][frontend] notifying backend /payment/algorand_pera/process');
            const response = await fetch('/payment/algorand_pera/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        tx_id: (processingValues && processingValues.tx_id) || (values && values.tx_id) || (this.paymentContext && this.paymentContext.txId) || null,
                        tx_hash: txid,
                        sender_address: connectedAddressValue,
                    }
                })
            });
            
                const responseData = await response.json().catch(() => ({}));
                // Unwrap JSON-RPC response
                const result = responseData.result || responseData;
                console.info('[Algorand][frontend] process response:', result);
                if (result && result.success) {
                    // Cart badge update: Handled automatically by Odoo
                    // When user navigates to /shop or /shop/cart after payment:
                    // 1. website_sale controller checks order.state
                    // 2. If state != 'draft', session['sale_order_id'] is cleared
                    // 3. Cart badge updates via page reload
                    // No manual DOM manipulation needed!
                    console.info('[Algorand][frontend] REDIRECTING TO /payment/status');
                    window.location.href = '/payment/status';
                    return;
                }
                
                // If backend process failed, show error
                throw new Error((result && result.message) || 'Payment processing failed');
            
        } catch (error) {
            
            // Show error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-2';
            
            if (error.message && error.message.includes('overspend')) {
                errorDiv.innerHTML = `
                    <strong>Payment Failed:</strong> Insufficient funds. Please add more ${values.currency_display_name || values.currency_name} to your wallet to complete this payment.
                `;
            } else {
                errorDiv.innerHTML = `
                    <strong>Payment Failed:</strong> ${error.message || 'Please try again or contact support if the problem persists.'}
                `;
            }
            
            const container = document.querySelector('[name="o_algorand_element_container"]') || document.body;
            container.appendChild(errorDiv);
            
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 8000);
        }
    },

    /**
     * Load Pera Wallet Connect SDK
     */
    async _loadPeraWalletConnect() {
        if (window.PeraWalletConnect) {
            return window.PeraWalletConnect;
        }
        const module = await import('https://esm.sh/@perawallet/connect@1.4.2?bundle');
        window.PeraWalletConnect = module.PeraWalletConnect || module.default;
        return window.PeraWalletConnect;
    },

            /**
            * Get Algorand form values
            */
            _getAlgorandFormValues() {
        // Get values from the payment context or form
        const inlineFormValues = document.querySelector('[name="o_algorand_element_container"]')?.getAttribute('data-algorand-inline-form-values');
        if (inlineFormValues) {
            const values = JSON.parse(inlineFormValues);
            
            // Try to get the current transaction ID from the payment context
            if (this.paymentContext && this.paymentContext.txId) {
                values.tx_id = this.paymentContext.txId;
            }
            
            return values;
        }
        
        // No inline form values found
        _logger.error('[Algorand] Cannot find inline form values - payment form not properly initialized');
        throw new Error('Payment form not properly initialized. Please refresh the page.');
    },

    // #=== DOM MANIPULATION ===#

    /**
     * Prepare the inline form of Algorand Pera Wallet for direct payment.
     *
     * @override method from @payment/js/payment_form
     * @private
     * @param {number} providerId - The id of the selected payment option's provider.
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {string} flow - The online payment flow of the selected payment option.
     * @return {void}
     */
            async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
                if (providerCode !== 'algorand_pera') {
                    await super._prepareInlineForm(...arguments);
                    return;
                }

        // Check if instantiation of the element is needed.
        if (this.algorandElements[paymentOptionId]) {
            this._setPaymentFlow('direct'); // Overwrite the flow even if no re-instantiation.
            return; // Don't re-instantiate if already done for this provider.
        }

                // Force the flow to be 'direct' for Algorand payments
                this._setPaymentFlow('direct');

                // Extract and deserialize the inline form values.
                const radio = document.querySelector('input[name="o_payment_radio"]:checked');
                const inlineForm = this._getInlineForm(radio);
                const algorandInlineForm = inlineForm.querySelector('[name="o_algorand_element_container"]');

                if (!algorandInlineForm) {
                    throw new Error("Algorand inline form container not found");
                }

        // Parse the inline form values
        const inlineFormValues = JSON.parse(algorandInlineForm.dataset.algorandInlineFormValues || '{}');
        
        // Create the Algorand payment UI
        this._renderAlgorandForm(algorandInlineForm, inlineFormValues);
        
        // Store reference for future use
        this.algorandElements[paymentOptionId] = algorandInlineForm;
    },

            _renderAlgorandForm(container, values) {
                const html = `
                    <div class="o_payment_algorand_pera">

                        <!-- Connect Wallet Section -->
                        <div class="text-center mb-4">
                            <button id="connect-pera-btn" class="btn btn-primary btn-lg px-4">
                                Connect Wallet
                            </button>
                        </div>

                        <!-- Wallet Info (Hidden initially) -->
                        <div id="wallet-info" class="d-none">
                            <!-- Connected Wallet Card -->
                            <div class="card border-success mb-4">
                                <div class="card-header bg-success text-white">
                                    <h6 class="mb-0">
                                        <i class="fas fa-check-circle me-2"></i>
                                        Wallet Connected
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div class="d-flex align-items-center">
                                        <div class="me-3">
                                            <div class="bg-light rounded-circle p-2">
                                                <i class="fas fa-wallet text-primary"></i>
                                            </div>
                                        </div>
                                        <div class="flex-grow-1">
                                            <small class="text-muted">Your Address</small>
                                            <div class="font-monospace small text-break" id="connected-address"></div>
                                            <div class="small mt-1"><span class="text-muted">Network:</span> <span id="algorand-network-name">${values.network === 'mainnet' ? 'MainNet' : 'TestNet'}</span></div>
                                        </div>
                                        <div>
                                            <button id="disconnect-pera-btn" class="btn btn-outline-secondary btn-sm ms-3">Disconnect</button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Payment Details Card -->
                            <div class="card mb-4">
                                <div class="card-header">
                                    <h6 class="mb-0">
                                        <i class="fas fa-receipt me-2"></i>
                                        Payment Details
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label small text-muted">Recipient Address</label>
                                            <div class="font-monospace small text-break bg-light p-2 rounded" id="recipient-address">${values.merchant_address}</div>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label small text-muted">Amount</label>
                                            <div class="h5 text-primary mb-0" id="amount-algo">${values.amount} ${values.currency_display_name || values.currency_name}</div>
                                        </div>
                                    </div>
                                    ${values.is_asa ? `
                                    <div id="asa-status" class="mt-2">
                                        <div class="alert alert-info d-flex align-items-center mb-2" role="alert">
                                            <i class="fas fa-info-circle me-2"></i>
                                            <div>
                                                To pay with ${values.currency_display_name || 'USDC'}, your wallet must be opted-in to the asset.
                                            </div>
                                        </div>
                                        <div class="d-flex gap-2">
                                            <button id="asa-optin-btn" class="btn btn-outline-primary btn-sm">
                                                Opt-in to ${values.currency_display_name || 'USDC'}
                                            </button>
                                            <span id="asa-optin-state" class="small text-muted"></span>
                                        </div>
                                        <div class="mt-2">
                                            <div id="merchant-asa-state" class="small text-muted"></div>
                                        </div>
                                    </div>
                                    ` : ''}
                                </div>
                            </div>

                            <!-- Pay Button -->
                            <div class="text-center">
                                <div class="alert alert-success mb-0">
                                    <i class="fas fa-check-circle me-2"></i>
                                    Wallet Ready for Payment
                                </div>
                            </div>

                            <!-- Security Notice -->
                            <div class="text-center mt-3">
                                <small class="text-muted">
                                    <i class="fas fa-shield-alt me-1"></i>
                                    Secured by Pera Wallet
                                </small>
                            </div>
                        </div>
                    </div>
                `;
        
        container.innerHTML = html;

        // Add event listeners
        this._setupAlgorandEventListeners(container, values);
    },

    _setupAlgorandEventListeners(container, values) {
        const connectBtn = container.querySelector('#connect-pera-btn');
        const walletInfo = container.querySelector('#wallet-info');
        const connectedAddress = container.querySelector('#connected-address');
        const asaStatus = container.querySelector('#asa-status');
        const asaOptinBtn = container.querySelector('#asa-optin-btn');
        const asaOptinState = container.querySelector('#asa-optin-state');
        const disconnectBtn = container.querySelector('#disconnect-pera-btn');
        const merchantAsaState = container.querySelector('#merchant-asa-state');

        let peraWallet = null;
        let connectedAddressValue = null;

        // Pay button state control (replaces algorand_inline_form.js)
        function getPayButton() {
            return document.querySelector('[name="o_payment_submit_button"], #o_payment_submit_button');
        }

        function updatePayButtonState() {
            const btn = getPayButton();
            if (!btn) return;
            
            // Only control the button when Algorand is the selected provider
            const selected = document.querySelector('input[name="o_payment_radio"]:checked');
            const isAlgorand = !!(selected && selected.dataset && selected.dataset.providerCode === 'algorand_pera');
            
            if (!isAlgorand) {
                btn.disabled = false;
                btn.removeAttribute('title');
                return;
            }
            
            // Check if wallet is connected
            const hasAddress = connectedAddressValue || (connectedAddress && connectedAddress.textContent.trim().length > 0);
            btn.disabled = !hasAddress;
            
            if (!hasAddress) {
                btn.setAttribute('title', 'Connect your wallet first');
            } else {
                btn.removeAttribute('title');
            }
        }

        // Observe address changes for pay button state
        if (connectedAddress && window.MutationObserver) {
            const observer = new MutationObserver(() => updatePayButtonState());
            observer.observe(connectedAddress, { childList: true, subtree: true, characterData: true });
        }

        async function loadPeraWalletConnect() {
            if (window.PeraWalletConnect) {
                return window.PeraWalletConnect;
            }
            const module = await import('https://esm.sh/@perawallet/connect@1.4.2?bundle');
            window.PeraWalletConnect = module.PeraWalletConnect || module.default;
            return window.PeraWalletConnect;
        }

        async function getAlgodClient() {
            const algosdk = await import('https://esm.sh/algosdk@3.5.2');
            return new algosdk.Algodv2('', values.node_url, '');
        }

        async function refreshSuggestedParams(algodClient) {
            const params = await algodClient.getTransactionParams().do();
            const minFee = Number(params.minFee ?? 1000);
            return {
                fee: minFee,
                flatFee: true,
                firstRound: Number(params.firstRound ?? params["first-round"] ?? params.firstValid),
                lastRound: Number(params.lastRound ?? params["last-round"] ?? params.lastValid),
                genesisID: params.genesisID,
                genesisHash: params.genesisHash
            };
        }

        async function isAsaOptedIn(address, assetId) {
            try {
                const algod = await getAlgodClient();
                const info = await algod.accountInformation(address).do();
                const assets = Array.isArray(info.assets) ? info.assets : (info["assets"] || []);
                return assets.some((a) => Number(a["asset-id"] ?? a.assetId ?? a["asset-id"]) === Number(assetId));
            } catch (e) {
                console.warn('ASA opt-in check failed:', e);
                return false;
            }
        }

        async function refreshMerchantAsaState() {
            if (!values.is_asa || !values.asset_id) {
                container.dataset.merchantAsaOptedIn = 'true';
                return;
            }
            const merchantAddress = values.merchant_address;
            if (!merchantAddress) return;
            const merchantOpted = await isAsaOptedIn(merchantAddress, values.asset_id);
            container.dataset.merchantAsaOptedIn = merchantOpted ? 'true' : 'false';
            if (merchantAsaState) {
                if (merchantOpted) {
                    merchantAsaState.textContent = `${values.currency_display_name || 'USDC'} is enabled for the merchant.`;
                    merchantAsaState.classList.remove('text-danger');
                } else {
                    merchantAsaState.textContent = `Merchant is not opted-in to ${values.currency_display_name || 'USDC'} yet. Payment cannot proceed.`;
                    merchantAsaState.classList.add('text-danger');
                }
            }
        }

        async function performAsaOptIn(address, assetId) {
            const algosdk = await import('https://esm.sh/algosdk@3.5.2');
            const algod = await getAlgodClient();
            const suggestedParams = await refreshSuggestedParams(algod);
            const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
                from: address,
                to: address,
                amount: 0,
                assetIndex: Number(assetId),
                suggestedParams,
            });
            const txnGroup = [{ txn }];
            const signed = await peraWallet.signTransaction(txnGroup);
            const res = await algod.sendRawTransaction(signed).do();
            const txid = res.txId || res.txid;
            // wait for confirmation (simple loop)
            try {
                const rounds = 8;
                let last = (await algod.status().do())["last-round"]; 
                for (let i = 0; i < rounds; i++) {
                    await algod.statusAfterBlock(++last).do();
                    const p = await algod.pendingTransactionInformation(txid).do();
                    if ((p["confirmed-round"] || 0) > 0) break;
                }
            } catch (_) {}
            return txid;
        }

        async function afterConnectEnsureAsaOptIn() {
            if (!values.is_asa || !values.asset_id) {
                container.dataset.asaOptedIn = 'true';
                return;
            }
            if (!connectedAddressValue) return;
            const opted = await isAsaOptedIn(connectedAddressValue, values.asset_id);
            container.dataset.asaOptedIn = opted ? 'true' : 'false';
            if (asaStatus) {
                if (opted) {
                    asaStatus.classList.remove('alert-warning');
                    if (asaOptinState) asaOptinState.textContent = 'USDC is opted-in and ready.';
                    if (asaOptinBtn) asaOptinBtn.classList.add('disabled');
                } else {
                    if (asaOptinState) asaOptinState.textContent = 'Not opted-in yet.';
                    if (asaOptinBtn) asaOptinBtn.classList.remove('disabled');
                }
            }
            // Also check merchant ASA state
            await refreshMerchantAsaState();
        }

        connectBtn.addEventListener('click', async function() {
                        connectBtn.disabled = true;
                        connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Connecting...';
            
            try {
                const PeraWalletConnect = await loadPeraWalletConnect();
                if (!peraWallet) {
                    const chainId = (values.network === 'mainnet') ? 416001 : 416002;
                    peraWallet = new PeraWalletConnect({ chainId });
                    window.peraWalletInstance = peraWallet; // Store globally
                }

                let accounts = [];
                try {
                    accounts = await peraWallet.reconnectSession();
                } catch (e) {
                    // Ignore, try full connect
                }

                if (!accounts || accounts.length === 0) {
                    if (peraWallet.isConnected) {
                        await peraWallet.disconnect();
                    }
                    accounts = await peraWallet.connect();
                }
                
                if (accounts && accounts.length > 0) {
                    connectedAddressValue = accounts[0];
                    connectedAddress.textContent = connectedAddressValue;
                    walletInfo.classList.remove('d-none');
                    connectBtn.innerHTML = 'Connect Wallet';
                    
                    // Update pay button state after connection
                    updatePayButtonState();
                    
                    // After connect, check ASA opt-in if required
                    await afterConnectEnsureAsaOptIn();
                } else {
                    throw new Error('No account connected');
                }

            } catch (error) {
                console.error('Pera connect failed:', error);
                alert('Pera connect failed: ' + (error && error.message ? error.message : error));
                connectBtn.innerHTML = 'Connect Wallet';
            } finally {
                connectBtn.disabled = false;
            }
        });

        if (disconnectBtn) {
            disconnectBtn.addEventListener('click', async function() {
                try {
                    if (peraWallet && peraWallet.isConnected) {
                        await peraWallet.disconnect();
                    }
                } catch (e) {
                    console.warn('Pera disconnect failed:', e);
                }
                connectedAddressValue = null;
                if (connectedAddress) connectedAddress.textContent = '';
                if (walletInfo) walletInfo.classList.add('d-none');
                container.dataset.asaOptedIn = 'false';
                if (asaOptinState) asaOptinState.textContent = '';
                connectBtn.innerHTML = 'Connect Wallet';
                
                // Update pay button state after disconnect
                updatePayButtonState();
            });
        }

        // Handle ASA opt-in button if present
        if (asaOptinBtn) {
            asaOptinBtn.addEventListener('click', async () => {
                if (!values.is_asa || !values.asset_id) return;
                if (!connectedAddressValue) return;
                try {
                    asaOptinBtn.disabled = true;
                    asaOptinBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Opting in...';
                    if (asaOptinState) asaOptinState.textContent = '';
                    const txid = await performAsaOptIn(connectedAddressValue, values.asset_id);
                    if (asaOptinState) asaOptinState.textContent = `Opt-in sent, tx: ${txid}`;
                    // Re-check opt-in state
                    await afterConnectEnsureAsaOptIn();
                    // Refresh merchant state as well
                    await refreshMerchantAsaState();
                } catch (e) {
                    console.error('ASA opt-in failed:', e);
                    if (asaOptinState) asaOptinState.textContent = 'Opt-in failed. Please try again.';
                } finally {
                    asaOptinBtn.disabled = false;
                    asaOptinBtn.innerHTML = `Opt-in to ${values.currency_display_name || 'USDC'}`;
                }
            });
        }

        // Initial pay button state check
        updatePayButtonState();
        
        // Listen for payment option changes
        document.addEventListener('change', (e) => {
            if (e.target && e.target.name === 'o_payment_radio') {
                updatePayButtonState();
            }
        });
    }
});