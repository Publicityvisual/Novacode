#!/usr/bin/env bash
# NovaCode CLI Local Automated Test Suite
set -euo pipefail

echo -e "[1;36m[NovaCode Test Suite][0m Running 47+ unit tests..."
python3 -m unittest discover tests -v
echo -e "[32m✓ All NovaCode tests passed successfully![0m"
