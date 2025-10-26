#!/bin/bash
# Simple reliable DMG creator

APP_NAME="PixelTraivo YT Downloader"
SOURCE_APP="dist/${APP_NAME}.app"
DMG_NAME="PixelTraivo-YT-Downloader-macOS.dmg"

echo "Creating DMG installer..."

# Cleanup
hdiutil detach "/Volumes/${APP_NAME}" -force 2>/dev/null || true
rm -f tmp.dmg "${DMG_NAME}"

# Verify app exists
if [ ! -d "$SOURCE_APP" ]; then
    echo "❌ ERROR: App not found at: $SOURCE_APP"
    exit 1
fi

# Create DMG directly (simple method)
hdiutil create \
    -volname "${APP_NAME}" \
    -srcfolder "$SOURCE_APP" \
    -ov \
    -format UDZO \
    "${DMG_NAME}"

if [ -f "${DMG_NAME}" ]; then
    echo "✅ DMG created: ${DMG_NAME}"
    ls -lh "${DMG_NAME}"
else
    echo "❌ ERROR: DMG creation failed"
    exit 1
fi