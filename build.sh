#!/bin/bash
# simple-build.sh

set -e

echo "🚀 Simple Build Starting..."

# Cleanup
rm -rf build dist *.dmg

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -q yt-dlp pyinstaller

# Build
echo "🔨 Building app..."

pyinstaller --name="PixelTraivo YT Downloader" \
    --windowed \
    --onefile \
    --noconfirm \
    --add-binary="$(which ffmpeg):." \
    --add-binary="$(which ffprobe):." \
    main.py

# For .app bundle (macOS specific)
if [ ! -d "dist/PixelTraivo YT Downloader.app" ]; then
    echo "Creating .app bundle..."
    
    # Rebuild as --onedir for proper .app
    pyinstaller --name="PixelTraivo YT Downloader" \
        --windowed \
        --onedir \
        --noconfirm \
        --add-binary="$(which ffmpeg):." \
        --add-binary="$(which ffprobe):." \
        main.py
fi

# Create simple DMG
echo "📀 Creating DMG..."

APP="dist/PixelTraivo YT Downloader.app"
DMG="PixelTraivo-YT-Downloader.dmg"

if [ -d "$APP" ]; then
    hdiutil create -volname "PixelTraivo YT Downloader" \
                   -srcfolder "$APP" \
                   -ov -format UDZO \
                   "$DMG"
    
    echo "✅ Done! DMG: $DMG"
    ls -lh "$DMG"
else
    echo "❌ App not found at: $APP"
    echo "Contents of dist/:"
    ls -la dist/
fi
