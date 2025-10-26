"""
Pixel Traivo YouTube Downloader
AutoSubs-inspired clean UI with all features
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import yt_dlp
import threading
import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# ========== SSL CERTIFICATE FIX ==========
import ssl
import certifi

# Set SSL certificate paths globally
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# For PyInstaller bundles
if getattr(sys, 'frozen', False):
    cert_path = certifi.where()
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path

# ========== FFMPEG PATH DETECTION ==========
def get_ffmpeg_path():
    """
    Get ffmpeg path for bundled or system installation
    Supports PyInstaller bundles and system installations
    """
    # Check if running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        
        # Check for bundled ffmpeg
        if sys.platform == 'darwin':  # macOS
            ffmpeg_path = os.path.join(base_path, 'ffmpeg')
            ffprobe_path = os.path.join(base_path, 'ffprobe')
        elif sys.platform == 'win32':  # Windows
            ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
            ffprobe_path = os.path.join(base_path, 'ffprobe.exe')
        else:  # Linux
            ffmpeg_path = os.path.join(base_path, 'ffmpeg')
            ffprobe_path = os.path.join(base_path, 'ffprobe')
        
        # Return directory if files exist
        if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
            return base_path
    
    # Check system PATH
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return os.path.dirname(system_ffmpeg)
    
    # Not found
    return None



# Console Logger Class
class ConsoleLogger:
    def __init__(self, app):
        self.app = app
    
    def debug(self, msg):
        if msg.startswith('[debug] '):
            return
        self.app.log(f"[DEBUG] {msg}")
    
    def info(self, msg):
        self.app.log(msg)
    
    def warning(self, msg):
        self.app.log(f"⚠️ {msg}")
    
    def error(self, msg):
        self.app.log(f"❌ {msg}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Traivo - YouTube Downloader")
        
        # Fixed window size - NO RESIZE
        self.window_width = 1100
        self.window_height = 900
        
        # Center and set fixed size
        self.center_window()
        
        # Disable resize
        self.root.resizable(False, False)
        
        # AutoSubs-inspired dark colors
        self.bg = "#0d1117"
        self.surface = "#161b22"
        self.border = "#30363d"
        self.accent = "#58a6ff"
        self.success = "#3fb950"
        self.error = "#f85149"
        self.text = "#c9d1d9"
        self.text_secondary = "#8b949e"
        
        self.root.configure(bg=self.bg)
        
        # Download path
        self.download_path = str(Path.home() / "Downloads" / "YouTube")
        Path(self.download_path).mkdir(parents=True, exist_ok=True)
        
        # Download history
        self.download_history = []
        
        # Check ffmpeg availability
        self.ffmpeg_path = get_ffmpeg_path()
        
        # Load saved settings
        self.load_settings()
        
        # Setup UI
        self.setup_ui()
        
        # Keyboard shortcuts
        self.setup_shortcuts()
        
        # Show ffmpeg status
        self.check_ffmpeg_status()
        
        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def check_ffmpeg_status(self):
        """Check and log ffmpeg availability"""
        if self.ffmpeg_path:
            self.log(f"✅ ffmpeg found at: {self.ffmpeg_path}")
        else:
            self.log("⚠️  ffmpeg not found - MP3 conversion may not work")
            self.log("   Install: brew install ffmpeg (macOS)")
    
    def center_window(self):
        """Center window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Command-v>', lambda e: self.url_entry.focus())
        self.root.bind('<Return>', lambda e: self.start_download())
        self.root.bind('<Command-q>', lambda e: self.on_closing())
        self.root.bind('<Command-l>', lambda e: self.clear_console())
    
    def load_settings(self):
        """Load saved settings"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.saved_quality = settings.get('quality', 'Best Quality')
                    self.saved_format = settings.get('format', 'MP4')
                    saved_path = settings.get('path')
                    if saved_path and os.path.exists(saved_path):
                        self.download_path = saved_path
        except:
            self.saved_quality = 'Best Quality'
            self.saved_format = 'MP4'
    
    def save_settings(self):
        """Save current settings"""
        try:
            settings = {
                'quality': self.quality_var.get(),
                'format': self.format_var.get(),
                'path': self.download_path
            }
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def on_closing(self):
        """Handle window close"""
        self.save_settings()
        self.root.quit()
    
    def setup_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill=tk.BOTH, expand=True, padx=40, pady=25)
        
        # Header section
        header = tk.Frame(main, bg=self.bg)
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header, text="▶", font=("Arial", 40, "bold"), 
                bg=self.bg, fg=self.accent).pack()
        
        tk.Label(header, text="Pixel Traivo YouTube Downloader", 
                font=("SF Pro Display", 22, "bold"), bg=self.bg, 
                fg=self.text).pack(pady=(5, 3))
        
        tk.Label(header, text="Download YouTube videos in high quality", 
                font=("SF Pro Display", 12), bg=self.bg, 
                fg=self.text_secondary).pack()
        
        # Separator
        separator = tk.Frame(main, height=1, bg=self.border)
        separator.pack(fill=tk.X, pady=15)
        
        # Input section
        input_section = tk.Frame(main, bg=self.bg)
        input_section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(input_section, text="YouTube URL", 
                font=("SF Pro Display", 11, "bold"), 
                bg=self.bg, fg=self.text).pack(anchor='w', pady=(0, 6))
        
        url_frame = tk.Frame(input_section, bg=self.surface, 
                            highlightbackground=self.border, 
                            highlightthickness=1)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var,
                                  font=("SF Pro Display", 12), 
                                  bg=self.surface, fg=self.text,
                                  relief=tk.FLAT, insertbackground=self.accent,
                                  borderwidth=0)
        self.url_entry.pack(fill=tk.X, padx=12, pady=10)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=...")
        self.url_entry.bind('<FocusIn>', self.on_url_focus_in)
        self.url_entry.bind('<FocusOut>', self.on_url_focus_out)
        
        # Options grid
        options_frame = tk.Frame(main, bg=self.bg)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Quality selection
        quality_frame = tk.Frame(options_frame, bg=self.bg)
        quality_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        tk.Label(quality_frame, text="Quality", 
                font=("SF Pro Display", 11, "bold"), 
                bg=self.bg, fg=self.text).pack(anchor='w', pady=(0, 6))
        
        quality_container = tk.Frame(quality_frame, bg=self.surface,
                                    highlightbackground=self.border,
                                    highlightthickness=1)
        quality_container.pack(fill=tk.X)
        
        self.quality_var = tk.StringVar(value=getattr(self, 'saved_quality', 'Best Quality'))
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TCombobox',
                       fieldbackground=self.surface,
                       background=self.surface,
                       foreground=self.text,
                       arrowcolor=self.text,
                       borderwidth=0,
                       relief=tk.FLAT)
        style.map('Custom.TCombobox',
                 fieldbackground=[('readonly', self.surface)],
                 selectbackground=[('readonly', self.surface)],
                 selectforeground=[('readonly', self.text)])
        
        quality_box = ttk.Combobox(quality_container, textvariable=self.quality_var,
                                  values=["Best Quality", "1080p", "720p", "480p", "Audio Only"],
                                  font=("SF Pro Display", 11), state='readonly',
                                  style='Custom.TCombobox')
        quality_box.pack(fill=tk.X, padx=10, pady=8)
        
        # Format selection
        format_frame = tk.Frame(options_frame, bg=self.bg)
        format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        tk.Label(format_frame, text="Format", 
                font=("SF Pro Display", 11, "bold"), 
                bg=self.bg, fg=self.text).pack(anchor='w', pady=(0, 6))
        
        format_container = tk.Frame(format_frame, bg=self.surface,
                                   highlightbackground=self.border,
                                   highlightthickness=1)
        format_container.pack(fill=tk.X)
        
        self.format_var = tk.StringVar(value=getattr(self, 'saved_format', 'MP4'))
        
        format_box = ttk.Combobox(format_container, textvariable=self.format_var,
                                 values=["MP4", "WEBM", "MP3"],
                                 font=("SF Pro Display", 11), state='readonly',
                                 style='Custom.TCombobox')
        format_box.pack(fill=tk.X, padx=10, pady=8)
        
        # Download button - CLEARLY VISIBLE
        btn_frame = tk.Frame(main, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create button with Canvas for better control
        self.download_btn_canvas = tk.Canvas(btn_frame, height=50, 
                                             bg=self.bg, highlightthickness=0)
        self.download_btn_canvas.pack(fill=tk.X)
        
        # Draw button background
        self.btn_rect = self.download_btn_canvas.create_rectangle(
            0, 0, 1020, 50, fill=self.accent, outline="", tags="btn_bg"
        )
        
        # Draw button text - BLACK COLOR FOR VISIBILITY
        self.btn_text = self.download_btn_canvas.create_text(
            510, 25, text="⬇ Download Video", 
            fill="#000000",  # BLACK TEXT - CLEARLY VISIBLE!
            font=("SF Pro Display", 14, "bold"), tags="btn_text"
        )
        
        # Button click handling
        self.download_btn_canvas.tag_bind("btn_bg", "<Button-1>", lambda e: self.start_download())
        self.download_btn_canvas.tag_bind("btn_text", "<Button-1>", lambda e: self.start_download())
        self.download_btn_canvas.bind("<Enter>", self.on_btn_hover)
        self.download_btn_canvas.bind("<Leave>", self.on_btn_leave)
        self.download_btn_canvas.config(cursor="hand2")
        
        # Progress section
        progress_container = tk.Frame(main, bg=self.surface,
                                     highlightbackground=self.border,
                                     highlightthickness=1)
        progress_container.pack(fill=tk.X, pady=(0, 15))
        
        progress_inner = tk.Frame(progress_container, bg=self.surface)
        progress_inner.pack(fill=tk.X, padx=15, pady=15)
        
        style.configure("Custom.Horizontal.TProgressbar",
                       troughcolor=self.bg,
                       background=self.accent,
                       thickness=8,
                       borderwidth=0)
        
        self.progress = ttk.Progressbar(progress_inner, mode='determinate',
                                       style="Custom.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(progress_inner, text="● Ready to download",
                                    font=("SF Pro Display", 11),
                                    bg=self.surface, fg=self.text_secondary,
                                    anchor='w')
        self.status_label.pack(fill=tk.X)
        
        # Console section with clear button
        console_header = tk.Frame(main, bg=self.bg)
        console_header.pack(fill=tk.X, pady=(0, 6))
        
        tk.Label(console_header, text="Console Output",
                font=("SF Pro Display", 11, "bold"),
                bg=self.bg, fg=self.text).pack(side=tk.LEFT)
        
        clear_btn = tk.Button(console_header, text="🗑️ Clear",
                             font=("SF Pro Display", 9),
                             bg=self.surface, fg=self.text,
                             relief=tk.FLAT, cursor="hand2",
                             command=self.clear_console,
                             padx=10, pady=2)
        clear_btn.pack(side=tk.RIGHT)
        
        log_container = tk.Frame(main, bg=self.border)
        log_container.pack(fill=tk.BOTH, expand=True)
        
        self.console = scrolledtext.ScrolledText(log_container,
                                                 font=("Menlo", 9),
                                                 bg=self.surface,
                                                 fg=self.text_secondary,
                                                 relief=tk.FLAT,
                                                 insertbackground=self.accent,
                                                 borderwidth=1,
                                                 height=12,
                                                 wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.console.insert("1.0", "● Pixel Traivo YouTube Downloader ready!\n")
        self.console.insert(tk.END, "● Paste a YouTube URL and press Enter or click Download\n")
        self.console.insert(tk.END, "● Shortcuts: ⌘+V (Paste), ⌘+L (Clear), ⌘+Q (Quit)\n")
        self.console.config(state=tk.DISABLED)
        
        # Footer with open folder button
        footer = tk.Frame(main, bg=self.bg)
        footer.pack(fill=tk.X, pady=(12, 0))
        
        footer_left = tk.Frame(footer, bg=self.bg)
        footer_left.pack(side=tk.LEFT)
        
        tk.Label(footer_left, text="📁 Save to: ",
                font=("SF Pro Display", 9),
                bg=self.bg, fg=self.text_secondary).pack(side=tk.LEFT)
        
        self.path_label = tk.Label(footer_left, text=self.download_path,
                                   font=("SF Pro Display", 9),
                                   bg=self.bg, fg=self.accent,
                                   cursor="hand2")
        self.path_label.pack(side=tk.LEFT, padx=5)
        self.path_label.bind("<Button-1>", lambda e: self.change_path())
        
        # Open folder button
        open_btn = tk.Button(footer_left, text="📂 Open",
                            font=("SF Pro Display", 9),
                            bg=self.surface, fg=self.accent,
                            relief=tk.FLAT, cursor="hand2",
                            command=self.open_download_folder,
                            padx=8, pady=2)
        open_btn.pack(side=tk.LEFT, padx=5)
        
        footer_right = tk.Frame(footer, bg=self.bg)
        footer_right.pack(side=tk.RIGHT)
        
        tk.Label(footer_right, text="Made with ❤️ by Pixel Traivo",
                font=("SF Pro Display", 9),
                bg=self.bg, fg=self.text_secondary).pack()
    
    def on_btn_hover(self, event):
        """Button hover effect"""
        self.download_btn_canvas.itemconfig(self.btn_rect, fill="#1f6feb")
    
    def on_btn_leave(self, event):
        """Button leave effect"""
        self.download_btn_canvas.itemconfig(self.btn_rect, fill=self.accent)
    
    def on_url_focus_in(self, event):
        if self.url_var.get() == "https://www.youtube.com/watch?v=...":
            self.url_entry.delete(0, tk.END)
    
    def on_url_focus_out(self, event):
        if not self.url_var.get():
            self.url_entry.insert(0, "https://www.youtube.com/watch?v=...")
    
    def log(self, message):
        """Log message to console"""
        self.console.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_console(self):
        """Clear console output"""
        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.insert('1.0', "● Console cleared.\n")
        self.console.config(state=tk.DISABLED)
        self.log("Console output cleared")
    
    def change_path(self):
        """Change download path"""
        path = filedialog.askdirectory(initialdir=self.download_path)
        if path:
            self.download_path = path
            self.path_label.config(text=path)
            self.log(f"📁 Download path changed to: {path}")
            self.save_settings()
    
    def open_download_folder(self):
        """Open download folder in Finder"""
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.download_path])
            elif sys.platform == 'win32':  # Windows
                subprocess.run(['explorer', self.download_path])
            else:  # Linux
                subprocess.run(['xdg-open', self.download_path])
            self.log(f"📂 Opened folder: {self.download_path}")
        except Exception as e:
            self.log(f"❌ Error opening folder: {e}")
    
    def start_download(self):
        """Start download process"""
        url = self.url_var.get().strip()
        if not url or url == "https://www.youtube.com/watch?v=...":
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        quality = self.quality_var.get()
        format_type = self.format_var.get()
        
        # Disable button
        self.download_btn_canvas.itemconfig(self.btn_text, text="Downloading...")
        self.download_btn_canvas.itemconfig(self.btn_rect, fill=self.text_secondary)
        
        thread = threading.Thread(target=self.download,
                                 args=(url, quality, format_type),
                                 daemon=True)
        thread.start()
    
    def download(self, url, quality, format_type):
        """Download video with real-time progress"""
        self.status_label.config(text="● Starting download...", fg=self.accent)
        self.progress['value'] = 0
        self.log("="*60)
        self.log(f"🚀 Starting download...")
        self.log(f"📎 URL: {url}")
        self.log(f"🎯 Quality: {quality}")
        self.log(f"📦 Format: {format_type}")
        self.log("-"*60)
        
        try:
            # Format selection
            if quality == "Audio Only" or format_type == "MP3":
                fmt = "bestaudio/best"
            elif quality == "1080p":
                fmt = "best[height<=1080]"
            elif quality == "720p":
                fmt = "best[height<=720]"
            elif quality == "480p":
                fmt = "best[height<=480]"
            else:
                fmt = "best"
            
            # Options with real-time progress
            ydl_opts = {
                'format': fmt,
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': False,
                'no_warnings': False,
                'logger': ConsoleLogger(self),
                'noprogress': False,
                'progress_with_newline': False,
            }
            
            # Add ffmpeg location if available
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
            
            # Audio conversion
            if format_type == "MP3" or quality == "Audio Only":
                if not self.ffmpeg_path:
                    self.log("⚠️  Warning: ffmpeg not found, MP3 conversion may fail")
                
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }]
            
            self.log("📡 Fetching video information...")
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Video')
                duration = info.get('duration', 0)
                filesize = info.get('filesize', 0)
            
            self.progress['value'] = 100
            self.status_label.config(text=f"✓ Download complete: {title[:35]}...",
                                   fg=self.success)
            
            size_mb = filesize / (1024 * 1024) if filesize else 0
            self.log("-"*60)
            self.log(f"✅ Successfully downloaded!")
            self.log(f"📝 Title: {title}")
            self.log(f"⏱️  Duration: {duration//60}m {duration%60}s")
            if size_mb > 0:
                self.log(f"💾 Size: {size_mb:.2f} MB")
            self.log(f"📁 Saved to: {self.download_path}")
            self.log("="*60)
            
            # Add to history
            self.download_history.append({
                'title': title,
                'url': url,
                'time': datetime.now().isoformat(),
                'path': self.download_path,
                'quality': quality,
                'format': format_type
            })
            
            # Save settings
            self.save_settings()
            
            messagebox.showinfo("Success",
                              f"Download complete!\n\n{title}\n\nSaved to:\n{self.download_path}")
        
        except Exception as e:
            self.progress['value'] = 0
            self.status_label.config(text=f"✗ Download failed", fg=self.error)
            self.log("-"*60)
            self.log(f"❌ Error: {str(e)}")
            self.log("="*60)
            messagebox.showerror("Download Failed", str(e))
        
        finally:
            # Re-enable button
            self.download_btn_canvas.itemconfig(self.btn_text, text="⬇ Download Video")
            self.download_btn_canvas.itemconfig(self.btn_rect, fill=self.accent)
    
    def progress_hook(self, d):
        """Progress callback - Real-time smooth update"""
        try:
            if d['status'] == 'downloading':
                # Try to get total bytes from multiple sources
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0 and downloaded > 0:
                    # Calculate percentage
                    percent = min((downloaded / total) * 100, 100)  # Cap at 100%
                    
                    # Update progress bar smoothly
                    self.progress['value'] = percent
                    
                    # Calculate sizes
                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total / (1024 * 1024)
                    
                    # Get speed and ETA
                    speed = d.get('speed', 0)
                    eta = d.get('eta', 0)
                    
                    if speed and speed > 0:
                        speed_mb = speed / (1024 * 1024)
                        
                        # Build status text
                        if eta:
                            mins, secs = divmod(eta, 60)
                            eta_text = f"{int(mins)}:{int(secs):02d}"
                            status_text = f"● Downloading... {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB) • {speed_mb:.2f} MB/s • ETA {eta_text}"
                        else:
                            status_text = f"● Downloading... {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB) • {speed_mb:.2f} MB/s"
                        
                        self.status_label.config(text=status_text, fg=self.accent)
                    else:
                        # No speed info
                        self.status_label.config(
                            text=f"● Downloading... {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)",
                            fg=self.accent)
                    
                    # Force immediate GUI update - THIS IS KEY!
                    self.progress.update()
                    self.status_label.update()
                    self.root.update()
                    
                else:
                    # Indeterminate progress (total unknown)
                    if downloaded > 0:
                        downloaded_mb = downloaded / (1024 * 1024)
                        speed = d.get('speed', 0)
                        
                        if speed and speed > 0:
                            speed_mb = speed / (1024 * 1024)
                            self.status_label.config(
                                text=f"● Downloading... {downloaded_mb:.1f} MB • {speed_mb:.2f} MB/s",
                                fg=self.accent)
                        else:
                            self.status_label.config(
                                text=f"● Downloading... {downloaded_mb:.1f} MB",
                                fg=self.accent)
                        
                        self.status_label.update()
                        self.root.update()
                        
            elif d['status'] == 'finished':
                # Download complete, processing
                self.progress['value'] = 100
                self.status_label.config(text="● Processing... (merging/converting)", fg=self.accent)
                self.log("⚙️  Download finished, processing file...")
                self.progress.update()
                self.status_label.update()
                self.root.update()
                
            elif d['status'] == 'error':
                self.log("❌ Download error occurred")
                
        except Exception as e:
            # Silent fail - don't interrupt download
            print(f"Progress hook error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()