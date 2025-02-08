#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Function to check if a command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✔ $1 passed${NC}"
        return 0
    else
        echo -e "${RED}✘ $1 failed${NC}"
        return 1
    fi
}

# Initialize error flag
ERROR=0

# Run Black
print_section "Running Black formatter"
black . --check
check_status "Black" || ERROR=1

# Run Flake8
print_section "Running Flake8"
flake8 .
check_status "Flake8" || ERROR=1

# Run tests with coverage
print_section "Running tests with coverage"
pytest --cov=core --cov-branch --cov-report=term-missing --cov-report=html
check_status "Tests" || ERROR=1

# Final summary
echo -e "\n${YELLOW}=== Summary ===${NC}"
if [ $ERROR -eq 0 ]; then
    echo -e "${GREEN}All checks passed! ✨ 🍰 ✨${NC}"
    echo "You can now push your changes."
else
    echo -e "${RED}Some checks failed. Please fix the issues before pushing.${NC}"
fi

exit $ERROR