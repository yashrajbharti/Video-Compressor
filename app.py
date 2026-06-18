import os
import re
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

class LosslessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Compressor")
        self.root.geometry("450x380")
        self.root.resizable(False, False)
        
        # UI Colors and Styling
        self.bg_color = "#0e1012"
        self.fg_color = "#EDEDED"
        self.accent_color = "#5667F5" # Purple from SVG
        self.font = ("Roboto", 17)      # Clean, large text
        self.root.configure(bg=self.bg_color)
        
        # Smooth interpolation variables
        self.target_percentage = 0.0
        self.display_percentage = 0.0
        self.is_compressing = False
        
        # macOS optimization: Support drag and drop onto the application icon in Dock/Finder
        try:
            self.root.createcommand("::tk::mac::OpenDocument", self.handle_open_document)
        except Exception:
            pass
            
        # Canvas for Vector Drawing (SVG alternative)
        self.canvas = tk.Canvas(root, width=450, height=280, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(pady=10)
        
        self.status_label = tk.Label(root, text="Click or Drop Video Here", font=self.font, bg=self.bg_color, fg=self.fg_color)
        self.status_label.pack(pady=5)
        
        # Load app icon image safely
        base_path = os.environ.get('RESOURCEPATH', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "icon-256.png")
        try:
            self.app_icon = tk.PhotoImage(file=icon_path) # Use native 256x256 size
        except:
            self.app_icon = None
            
        # Bind click to open file dialog
        self.canvas.bind("<Button-1>", self.browse_file)
        self.status_label.bind("<Button-1>", self.browse_file)
        self.root.bind("<Button-1>", self.browse_file)
        
        # Setup drag and drop for window
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_dnd_drop)
        
        self.draw_idle_icon()
        
    def draw_idle_icon(self):
        self.canvas.delete("all")
        cx, cy = 225, 140
        if self.app_icon:
            self.canvas.create_image(cx, cy, image=self.app_icon, tags="clickable")
        else:
            # Fallback
            self.canvas.create_text(cx, cy, text="ICON", fill=self.fg_color, font=self.font)
        
    def smooth_update_loop(self):
        """High-frequency 60FPS loop that smoothly glides the UI to the target value"""
        if not self.is_compressing:
            return

        diff = self.target_percentage - self.display_percentage
        
        if abs(diff) > 0.05:
            self.display_percentage += diff * 0.1
        else:
            self.display_percentage = self.target_percentage

        # Render the current state of the glide
        self.draw_loader(self.display_percentage)

        # Schedule next frame update in 16ms (~60 frames per second)
        self.root.after(16, self.smooth_update_loop)

    def draw_loader(self, percentage):
        self.canvas.delete("all")
        cx, cy = 225, 140
        r = 100
        # Background circle
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#2a2d35", width=6)
        # Progress arc (cap at 359.99 because Tkinter arcs disappear at 360)
        extent = -(percentage / 100.0) * 359.99
        if extent != 0:
            self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=90, extent=extent, style=tk.ARC, outline=self.accent_color, width=6)
        # Percentage text 
        self.canvas.create_text(cx, cy, text=f"{int(percentage)}%", fill=self.fg_color, font=("Roboto", 38, "bold"))
        
    def draw_done_icon(self):
        self.canvas.delete("all")
        cx, cy = 225, 140
        r = 100
        # Circle
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=self.accent_color, width=6)
        # Checkmark
        self.canvas.create_line(cx-30, cy, cx-10, cy+30, cx+40, cy-30, fill=self.accent_color, width=8, capstyle=tk.ROUND, joinstyle=tk.ROUND)

    def handle_open_document(self, *args):
        if not self.is_compressing:
            for arg in args:
                self.process_file(arg)

    def handle_dnd_drop(self, event):
        if self.is_compressing: return
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.process_file(file_path)

    def browse_file(self, event=None):
        if self.is_compressing: return
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv *.webm *.*")])
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        if os.path.isfile(file_path):
            self.is_compressing = True
            self.target_percentage = 0.0
            self.display_percentage = 0.0
            self.status_label.config(text="Compressing...")
            
            # Fire up the rendering loops
            self.smooth_update_loop()
            threading.Thread(target=self.compress_video, args=(file_path,), daemon=True).start()

    def get_duration(self, file_path):
        # Try format duration first
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.get_env())
            val = res.stdout.strip()
            if val and val != "N/A":
                return float(val)
        except:
            pass
            
        # Try stream duration next if format duration fails/returns N/A
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.get_env())
            val = res.stdout.strip()
            if val and val != "N/A":
                return float(val)
        except:
            pass
            
        return 1.0

    def get_env(self):
        env = os.environ.copy()
        env["PATH"] = f"/opt/homebrew/bin:/usr/local/bin:{env.get('PATH', '')}"
        return env

    def compress_video(self, input_path):
        dir_name = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}_compressed.webm")
        
        total_duration = self.get_duration(input_path)
        cmd = ["ffmpeg", "-y", "-i", input_path, "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-c:a", "libopus", output_path]
        process = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True, env=self.get_env())
        
        time_regex = re.compile(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)")
        buffer = ""
        
        while True:
            char = process.stdout.read(1)
            if not char and process.poll() is not None: break
            
            if char in ('\r', '\n'):
                match = time_regex.search(buffer)
                if match:
                    hours, minutes, seconds = map(float, match.groups())
                    current_time = (hours * 3600) + (minutes * 60) + seconds
                    
                    # Update target percentage with rounding to stay precise
                    self.target_percentage = min(round((current_time / total_duration) * 100), 100)
                buffer = ""
            else:
                buffer += char
                
        process.wait()
        
        if process.returncode == 0:
            # Overrule thread values to hold a true 100% state
            self.target_percentage = 100.0
            self.display_percentage = 100.0
            
            # Force target layout re-paint right onto the main thread safely
            self.root.after_idle(lambda: self.draw_loader(100.0))
            
            # Give UI thread a 400ms visual buffer to draw 100% before popup interrupts
            self.root.after(400, self.finish_success, output_path)
        else:
            self.root.after(0, self.finish_error)

    def finish_success(self, output_path):
        self.is_compressing = False
        self.draw_done_icon()
        self.status_label.config(text="Compression Complete!")
        messagebox.showinfo("Success", f"Compressed WebM video saved to:\n{output_path}")
        self.reset_ui()
        
    def finish_error(self):
        self.is_compressing = False
        self.draw_idle_icon()
        self.status_label.config(text="Compression Failed.")
        messagebox.showerror("Error", "Compression failed. Check if FFmpeg is installed.")
        self.reset_ui()
        
    def reset_ui(self):
        self.is_compressing = False
        self.draw_idle_icon()
        self.status_label.config(text="Click or Drop Video Here")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = LosslessApp(root)
    root.mainloop()
