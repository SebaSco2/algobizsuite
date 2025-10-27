* SebaSco2 <sebascotti.uru@gmail.com>

## Development Tools

### Coding Standards Compliance

The project includes a compliance check script at the root level: `check_compliance.sh`

**Usage:**
```bash
cd /path/to/algobizsuite
./check_compliance.sh
```

**What it checks:**
- Python syntax validation
- Black code formatting (PEP 8 compliant, 88-char line length)
- flake8 linting
- ESLint for JavaScript

**Configuration files:**
- `.flake8` - Python linting configuration
- `.eslintrc.json` - JavaScript linting configuration
- `pyproject.toml` - Black formatter configuration

**Install optional tools:**
```bash
pip install black flake8
npm install -g eslint
```

Run this script before committing to ensure code quality standards.
