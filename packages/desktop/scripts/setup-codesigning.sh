#!/usr/bin/env bash
set -euo pipefail

echo "=== NovaCode Code Signing Setup ==="
echo ""

# Check if codesigning is available
if security find-identity -v -p codesigning | grep -q "valid identities found"; then
  echo "✓ Code signing identities found:"
  security find-identity -v -p codesigning | grep "valid identities found" -A 5
  echo ""
  echo "To use a Developer ID, update electron-builder.config.ts:"
  echo '  mac: {'
  echo "    identity: \"Developer ID Application: Your Name (TEAM_ID)\","
  echo "    notarize: true,"
  echo "  }"
else
  echo "⚠ No valid code signing identities found."
  echo ""
  echo "Options:"
  echo ""
  echo "1. Use ad-hoc signing (current setup):"
  echo "   - App will work but macOS may show warnings"
  echo "   - Good for internal/development use"
  echo "   - Already configured in electron-builder.config.ts"
  echo ""
  echo "2. Get a Developer ID from Apple:"
  echo "   - Go to https://developer.apple.com/account/"
  echo "   - Enroll in Apple Developer Program (\$99/year)"
  echo "   - Create a 'Developer ID Application' certificate"
  echo "   - Update electron-builder.config.ts with your identity"
  echo ""
  echo "3. Use a self-signed certificate:"
  echo "   - Open Keychain Access"
  echo "   - Create a new certificate: 'NovaCode Development'"
  echo "   - Set 'Code Signing' as the certificate type"
  echo "   - Update electron-builder.config.ts:"
  echo '     mac: {'
  echo "       identity: \"NovaCode Development\","
  echo "       notarize: false,"
  echo "     }"
  echo ""
fi

echo ""
echo "Current configuration:"
echo "  - hardenedRuntime: true"
echo "  - notarize: false (ad-hoc signing)"
echo "  - gatekeeperAssess: false"
echo ""
echo "To enable notarization, you need:"
echo "  1. Apple Developer Program membership"
echo "  2. Developer ID Application certificate"
echo "  3. App-specific password for notarization"
echo ""
