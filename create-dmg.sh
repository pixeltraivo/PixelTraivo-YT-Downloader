#!/bin/bash

# Simple DMG creator without create-dmg dependency

APP_NAME="PixelTraivo YT Downloader"
DMG_NAME="PixelTraivo-YT-Downloader-macOS"
SOURCE_APP="dist/${APP_NAME}.app"
TMP_DMG="tmp.dmg"
FINAL_DMG="${DMG_NAME}.dmg"

# Create temporary DMG
echo "Creating temporary DMG..."
hdiutil create -size 500m -fs HFS+ -volname "${APP_NAME}" "${TMP_DMG}"

# Mount it
echo "Mounting DMG..."
hdiutil attach "${TMP_DMG}" -mountpoint /Volumes/"${APP_NAME}"

# Copy app
echo "Copying app..."
cp -R "${SOURCE_APP}" /Volumes/"${APP_NAME}"/

# Create Applications symlink
echo "Creating Applications link..."
ln -s /Applications /Volumes/"${APP_NAME}"/Applications

# Unmount
echo "Unmounting..."
hdiutil detach /Volumes/"${APP_NAME}"

# Convert to compressed
echo "Compressing DMG..."
hdiutil convert "${TMP_DMG}" -format UDZO -o "${FINAL_DMG}"

# Cleanup
rm "${TMP_DMG}"

echo "✅ DMG created: ${FINAL_DMG}"