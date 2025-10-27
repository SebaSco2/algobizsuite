#!/bin/bash

# Coding Standards Compliance Check Script
# Checks Python and JavaScript code against defined standards

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   Coding Standards Compliance Check${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Track overall status
ERRORS=0

# Check if tools are installed
echo -e "${BLUE}Checking required tools...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ python3 not found${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ python3 found${NC}"
fi

if ! python3 -m black --version &> /dev/null; then
    echo -e "${YELLOW}⚠ black not installed (run: pip install black)${NC}"
    BLACK_AVAILABLE=0
else
    echo -e "${GREEN}✓ black found${NC}"
    BLACK_AVAILABLE=1
fi

if ! python3 -m flake8 --version &> /dev/null; then
    echo -e "${YELLOW}⚠ flake8 not installed (run: pip install flake8)${NC}"
    FLAKE8_AVAILABLE=0
else
    echo -e "${GREEN}✓ flake8 found${NC}"
    FLAKE8_AVAILABLE=1
fi

if ! command -v eslint &> /dev/null; then
    echo -e "${YELLOW}⚠ eslint not installed (run: npm install -g eslint)${NC}"
    ESLINT_AVAILABLE=0
else
    echo -e "${GREEN}✓ eslint found${NC}"
    ESLINT_AVAILABLE=1
fi

echo ""

# Python Syntax Check
echo -e "${BLUE}[1/4] Checking Python syntax...${NC}"
PYTHON_FILES=$(find addons -name "*.py" -not -path "*/migrations/*" -not -path "*/__pycache__/*" 2>/dev/null)
SYNTAX_ERRORS=0

for file in $PYTHON_FILES; do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${RED}  ✗ Syntax error: $file${NC}"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        ERRORS=$((ERRORS + 1))
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    FILE_COUNT=$(echo "$PYTHON_FILES" | wc -l | tr -d ' ')
    echo -e "${GREEN}  ✓ All $FILE_COUNT Python files have valid syntax${NC}"
else
    echo -e "${RED}  ✗ Found $SYNTAX_ERRORS syntax errors${NC}"
fi
echo ""

# Black Formatting Check
if [ $BLACK_AVAILABLE -eq 1 ]; then
    echo -e "${BLUE}[2/4] Checking Black formatting...${NC}"
    if python3 -m black --check --line-length 88 addons/ 2>&1 | grep -q "would be reformatted"; then
        echo -e "${RED}  ✗ Some files need formatting${NC}"
        echo -e "${YELLOW}  Run: black --line-length 88 addons/${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ All files are properly formatted${NC}"
    fi
else
    echo -e "${YELLOW}[2/4] Skipping Black check (not installed)${NC}"
fi
echo ""

# Flake8 Linting
if [ $FLAKE8_AVAILABLE -eq 1 ]; then
    echo -e "${BLUE}[3/4] Running flake8 linting...${NC}"
    if python3 -m flake8 addons/ 2>&1 | grep -q ":"; then
        echo -e "${RED}  ✗ Linting issues found${NC}"
        python3 -m flake8 addons/ | head -20
        echo -e "${YELLOW}  (showing first 20 issues)${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}  ✓ No linting issues found${NC}"
    fi
else
    echo -e "${YELLOW}[3/4] Skipping flake8 check (not installed)${NC}"
fi
echo ""

# ESLint Check
if [ $ESLINT_AVAILABLE -eq 1 ]; then
    echo -e "${BLUE}[4/4] Running ESLint...${NC}"
    JS_FILES=$(find addons -name "*.js" -not -path "*/lib/*" 2>/dev/null)
    if [ -n "$JS_FILES" ]; then
        ESLINT_OUTPUT=$(eslint $JS_FILES 2>&1)
        # Check for actual errors (not warnings)
        if echo "$ESLINT_OUTPUT" | grep -E "^.*:[0-9]+:[0-9]+.*error" > /dev/null; then
            echo -e "${RED}  ✗ JavaScript errors found${NC}"
            echo "$ESLINT_OUTPUT" | head -20
            echo -e "${YELLOW}  (showing first 20 issues)${NC}"
            ERRORS=$((ERRORS + 1))
        elif echo "$ESLINT_OUTPUT" | grep -q "warning"; then
            echo -e "${YELLOW}  ⚠ JavaScript warnings found (non-critical)${NC}"
            WARN_COUNT=$(echo "$ESLINT_OUTPUT" | grep -c "warning" || echo "0")
            echo -e "${YELLOW}  $WARN_COUNT warnings - consider fixing for best practices${NC}"
        else
            echo -e "${GREEN}  ✓ No JavaScript linting issues${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠ No JavaScript files found${NC}"
    fi
else
    echo -e "${YELLOW}[4/4] Skipping ESLint check (not installed)${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}=====================================${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All compliance checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS compliance issues${NC}"
    echo -e "${YELLOW}Please fix the issues and run again${NC}"
    exit 1
fi

