"""
Icon Generator - PNG to ICNS/ICO
"""

from PIL import Image
import os

def generate_icons():
    """Generate .icns and .ico from logo.png"""
    
    logo_path = "assets/logo.png"
    
    if not os.path.exists(logo_path):
        print("❌ logo.png not found!")
        return
    
    print("📐 Loading logo.png...")
    img = Image.open(logo_path)
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Generate Windows ICO (256x256, 128x128, 64x64, 32x32, 16x16)
    print("🪟 Generating Windows icon...")
    ico_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    img.save('assets/icon.ico', format='ICO', sizes=ico_sizes)
    print("✅ Created: assets/icon.ico")
    
    # Generate macOS ICNS (need to use iconutil on macOS)
    print("🍎 Generating macOS icon...")
    
    # Create iconset folder
    iconset_path = "assets/icon.iconset"
    os.makedirs(iconset_path, exist_ok=True)
    
    # macOS icon sizes
    sizes = {
        'icon_16x16.png': (16, 16),
        'icon_16x16@2x.png': (32, 32),
        'icon_32x32.png': (32, 32),
        'icon_32x32@2x.png': (64, 64),
        'icon_128x128.png': (128, 128),
        'icon_128x128@2x.png': (256, 256),
        'icon_256x256.png': (256, 256),
        'icon_256x256@2x.png': (512, 512),
        'icon_512x512.png': (512, 512),
        'icon_512x512@2x.png': (1024, 1024),
    }
    
    for filename, size in sizes.items():
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(os.path.join(iconset_path, filename))
        print(f"  ✓ {filename}")
    
    # Convert to icns using iconutil (macOS only)
    import subprocess
    try:
        subprocess.run([
            'iconutil', '-c', 'icns', iconset_path,
            '-o', 'assets/icon.icns'
        ], check=True)
        print("✅ Created: assets/icon.icns")
        
        # Cleanup iconset folder
        import shutil
        shutil.rmtree(iconset_path)
        print("🧹 Cleaned up temporary files")
        
    except FileNotFoundError:
        print("⚠️  iconutil not found (macOS only)")
        print("   Keeping iconset folder for manual conversion")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print("\n✅ Icon generation complete!")

if __name__ == "__main__":
    generate_icons()