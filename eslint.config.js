// ESLint v9+ configuration
export default [
    {
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: 'module',
            globals: {
                // Browser globals
                console: 'readonly',
                document: 'readonly',
                window: 'readonly',
                setTimeout: 'readonly',
                clearTimeout: 'readonly',
                setInterval: 'readonly',
                clearInterval: 'readonly',
                fetch: 'readonly',
                TextEncoder: 'readonly',
                TextDecoder: 'readonly',
                MutationObserver: 'readonly',
                alert: 'readonly',
                // Odoo globals
                odoo: 'readonly',
                // Library globals
                algosdk: 'readonly',
                _: 'readonly',
                _t: 'readonly',
                _logger: 'readonly'
            }
        },
        rules: {
            'no-unused-vars': ['warn', { 
                'argsIgnorePattern': '^_',
                'varsIgnorePattern': '^_|^algosdk$|^e$'
            }],
            'no-console': 'off',
            'no-undef': 'warn'
        }
    }
];
