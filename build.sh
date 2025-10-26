#!/bin/bash
# PixelTraivo YT Downloader - macOS Build Script

set -e  # Exit on error

echo "🚀 PixelTraivo YouTube Downloader - Build Starting..."
echo ""

# ========== CLEANUP ==========
echo "🧹 Cleaning up old builds..."
rm -rf build dist *.dmg
echo "✅ Cleanup done"
echo ""

# ========== SETUP ENVIRONMENT ==========
echo "📦 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q pyinstaller
echo "✅ Environment ready"
echo ""

# ========== CHECK FFMPEG ==========
echo "🔍 Checking for ffmpeg..."
FFMPEG_PATH=$(which ffmpeg || echo "")
FFPROBE_PATH=$(which ffprobe || echo "")

if [ -z "$FFMPEG_PATH" ] || [ -z "$FFPROBE_PATH" ]; then
    echo "❌ ERROR: ffmpeg/ffprobe not found!"
    echo ""
    echo "Install with: brew install ffmpeg"
    exit 1
fi

echo "✅ ffmpeg found at: $FFMPEG_PATH"
echo "✅ ffprobe found at: $FFPROBE_PATH"
echo ""

# ========== CHECK ICON ==========
if [ ! -f "assets/icon.icns" ]; then
    echo "⚠️  Warning: icon.icns not found, building without icon"
    ICON_ARG=""
else
    echo "✅ Icon found: assets/icon.icns"
    ICON_ARG="--icon=assets/icon.icns"
fi
echo ""

# ========== BUILD APP ==========
echo "🔨 Building macOS application..."
pyinstaller \
    --name="PixelTraivo YT Downloader" \
    --windowed \
    --onedir \
    --noconfirm \
    --clean \
    $ICON_ARG \
    --add-binary="$FFMPEG_PATH:." \
    --add-binary="$FFPROBE_PATH:." \
    --add-data="assets:assets" \
    --hidden-import=yt_dlp \
    --hidden-import=tkinter \
    --osx-bundle-identifier=com.pixeltraivo.ytdownloader \
    main.py

echo "✅ Build complete!"
echo ""

# ========== VERIFY BUILD ==========
APP_PATH="dist/PixelTraivo YT Downloader.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ ERROR: App bundle not created!"
    echo "Expected: $APP_PATH"
    echo ""
    echo "Contents of dist/:"
    ls -la dist/
    exit 1
fi

echo "✅ App bundle created: $APP_PATH"
echo ""

# ========== CREATE DMG ==========
echo "📀 Creating DMG installer..."
DMG_NAME="PixelTraivo-YT-Downloader-macOS.dmg"

# Run the DMG creation script
if [ -f "create-dmg.sh" ]; then
    chmod +x create-dmg.sh
    ./create-dmg.sh
else
    # Fallback: Simple DMG creation
    hdiutil create \
        -volname "PixelTraivo YT Downloader" \
        -srcfolder "$APP_PATH" \
        -ov \
        -format UDZO \
        "$DMG_NAME"
fi

echo ""
echo "=========================================="
echo "✅ BUILD SUCCESSFUL!"
echo "=========================================="
echo ""
echo "📦 Application: $APP_PATH"
if [ -f "$DMG_NAME" ]; then
    echo "📀 DMG Installer: $DMG_NAME"
    echo ""
    ls -lh "$DMG_NAME"
fi
echo ""
echo "🧪 Test the app:"
echo "   open \"$APP_PATH\""
echo ""