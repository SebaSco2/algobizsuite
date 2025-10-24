# -*- coding: utf-8 -*-

def migrate(cr, version):
    """Migrate existing payment transactions to use the new payment method."""
    
    # Check if there are any existing payment transactions with the old method
    cr.execute("""
        SELECT id FROM payment_transaction 
        WHERE payment_method_id IN (
            SELECT id FROM payment_method 
            WHERE code = 'algorand_pera' AND name != 'Algorand (Pera Wallet)'
        )
    """)
    
    old_transactions = cr.fetchall()
    
    if old_transactions:
        # Update the payment method name for existing transactions
        cr.execute("""
            UPDATE payment_method 
            SET name = 'Algorand (Pera Wallet)',
                active = true
            WHERE code = 'algorand_pera'
        """)
        
        # Update any existing payment provider
        cr.execute("""
            UPDATE payment_provider 
            SET name = 'Algorand Pera Wallet',
                state = 'enabled',
                is_published = true
            WHERE code = 'algorand_pera'
        """)
