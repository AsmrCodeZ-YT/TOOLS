import customtkinter as ctk
import os
import threading

# Initialize the app theme
ctk.set_appearance_mode("System")  # "Dark", "Light", or "System"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class YouTubeCommentDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Comment Downloader")
        self.geometry("500x300")
        self.resizable(False, False)

        # Title Label
        self.title_label = ctk.CTkLabel(self, text="YouTube Comment Downloader", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        # URL Input
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Enter YouTube Video URL", width=400)
        self.url_entry.pack(pady=10)

        # Download Button
        self.download_button = ctk.CTkButton(self, text="Download Comments", command=self.start_download)
        self.download_button.pack(pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

    def start_download(self):
        video_url = self.url_entry.get().strip()
        if not video_url:
            self.status_label.configure(text="❌ Please enter a valid URL.", text_color="red")
            return

        self.status_label.configure(text="⏳ Downloading comments...", text_color="orange")
        threading.Thread(target=self.download_comments, args=(video_url,), daemon=True).start()

    def download_comments(self, video_url):
        command = f'youtube-comment-downloader --url "{video_url}" --output comments.json'
        result = os.system(command)

        if result == 0:
            self.status_label.configure(text="✅ Comments saved successfully!", text_color="green")
        else:
            self.status_label.configure(text="❌ Error: Could not download comments.", text_color="red")

if __name__ == "__main__":
    app = YouTubeCommentDownloader()
    app.mainloop()
