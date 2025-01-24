import os
import sys
import time
import subprocess
import threading
from threading import Thread, Lock
from queue import Queue
import requests
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
import tkinter as tk
from colorama import Fore, Back, Style, init
import json
import re
from mutagen.flac import FLAC, Picture
from PIL import Image
from io import BytesIO

# Constants
MAX_WAIT_TIME = 25  # seconds
MAX_THREADS = 5  # adjust number of threads as desired

# Global variables for threading
download_queue = Queue()
lock = threading.Lock()

# Global variables for tracking errors and failures
errors = []
failed_count = 0

total_songs = 0
songs_downloaded = 0
failed_downloads = 0
start_time = time.time()


def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours > 0:
        return f"{hours} hours {minutes} minutes"
    else:
        return f"{minutes} minutes"


def update_status():
    global songs_downloaded, start_time
    elapsed_time = time.time() - start_time
    average_time_per_song = elapsed_time / max(songs_downloaded, 1)
    estimated_remaining_time = average_time_per_song * (total_songs - songs_downloaded)
    active_threads = threading.active_count()

    os.system('cls' if os.name == 'nt' else 'clear')
    print(
        Fore.WHITE +
        Back.BLUE +
        f"ETA: {format_time(estimated_remaining_time)} " +
        Fore.RESET +
        Back.RESET +
        " | " +
        Fore.WHITE +
        Back.BLUE +
        f"Threads: {active_threads} " +
        Fore.RESET +
        Back.RESET +
        " | " +
        Fore.WHITE +
        Back.BLUE +
        f"Downloaded: {songs_downloaded}/{total_songs} " +
        Fore.RESET +
        Back.RESET +
        " | " +
        Fore.WHITE +
        Back.RED +
        f"Failed: {failed_downloads}" +
        Fore.RESET +
        Back.RESET)


def install_required_modules():
    required_modules = [
        "requests",
        "customtkinter",
        "tkinter",
        "colorama",
        "datetime",
        "json",
    ]
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", module])


def download_song(artist, song):
    global failed_count, errors, songs_downloaded, failed_downloads
    service_url = "https://us.qobuz.squid.wtf"
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            time.sleep(1)
            search_url = f"{service_url}/api/get-music?q={song}%20-%20{artist}&offset=0"
            print(f"\nSearching URL: {search_url}")
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()['data']
            tracks = []
            if 'most_popular' in data:
                tracks = [item['content'] for item in data['most_popular'].get('items', [])
                         if item.get('type') == 'tracks']
            
            if not tracks:
                raise ValueError("No tracks found")

            track = None
            for t in tracks:
                performer = t.get('performer', {}).get('name', '').lower()
                if performer == artist.lower():
                    track = t
                    break
            
            if not track:
                raise ValueError(f"No matching track found for '{song}' by '{artist}'")

            track_id = track.get('id')
            if not track_id:
                raise ValueError("Track ID not found")
                
            download_url = f"{service_url}/api/download-music?track_id={track_id}&quality=27"
            print(f"\nDownload URL: {download_url}")
            
            download_response = requests.get(download_url, stream=True, timeout=30)
            download_response.raise_for_status()
            
            streaming_data = download_response.json()
            if not streaming_data.get('success') or 'data' not in streaming_data or 'url' not in streaming_data['data']:
                raise ValueError("Failed to get streaming URL")
                
            streaming_url = streaming_data['data']['url']
            print(f"\nStreaming URL obtained, downloading...")
            
            stream_response = requests.get(streaming_url, stream=True, timeout=30)
            stream_response.raise_for_status()
            
            real_artist = track.get('performer', {}).get('name', artist)
            real_title = track.get('title', song).replace(" (Explicit Version)", "").replace(" (Album Version)", "")
            real_artist = re.sub(r'[<>:"/\\|?*]', '', real_artist)
            real_title = re.sub(r'[<>:"/\\|?*]', '', real_title)
            
            filename = f"{real_artist} - {real_title}.flac"
            filepath = os.path.join(app.download_directory, filename)
            
            total_size = int(stream_response.headers.get('content-length', 0))
            if total_size < 1000000:
                raise ValueError("File size too small for a FLAC file")

            with open(filepath, 'wb') as f:
                downloaded_size = 0
                for chunk in stream_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rDownloading {filename}: {progress:.1f}%", end='')

            try:
                audio = FLAC(filepath)
                
                # Basic metadata
                audio['title'] = real_title
                audio['artist'] = real_artist
                
                # Album metadata
                if track.get('album'):
                    audio['album'] = track['album'].get('title', '')
                    audio['date'] = str(track['album'].get('release_date_original', ''))
                    if track['album'].get('label'):
                        audio['label'] = track['album']['label'].get('name', '')
                    if track['album'].get('genre'):
                        audio['genre'] = track['album']['genre'].get('name', '')
                    if track['album'].get('upc'):
                        audio['upc'] = track['album'].get('upc', '')
                
                # Track metadata
                if track.get('isrc'):
                    audio['isrc'] = track['isrc']
                if track.get('track_number'):
                    audio['tracknumber'] = str(track['track_number'])
                if track.get('disc_number'):
                    audio['discnumber'] = str(track['disc_number'])
                if track.get('duration'):
                    audio['length'] = str(track['duration'])
                if track.get('copyright'):
                    audio['copyright'] = track['copyright']
                if track.get('composer'):
                    audio['composer'] = track['composer'].get('name', '')
                if track.get('performers'):
                    audio['performers'] = track['performers']
                
                # Technical metadata
                if track.get('maximum_bit_depth'):
                    audio['bit_depth'] = str(track['maximum_bit_depth'])
                if track.get('maximum_sampling_rate'):
                    audio['sample_rate'] = str(track['maximum_sampling_rate'])
                if track.get('maximum_channel_count'):
                    audio['channels'] = str(track['maximum_channel_count'])
                
                # Album Art (highest quality available)
                if track['album'].get('image'):
                    img_url = None
                    for size in ['large', 'extralarge', 'mega']:
                        if track['album']['image'].get(size):
                            img_url = track['album']['image'][size]
                            break
                    
                    if img_url:
                        img_response = requests.get(img_url)
                        img_response.raise_for_status()
                        
                        picture = Picture()
                        picture.type = 3
                        picture.mime = "image/jpeg"
                        picture.desc = "Cover"
                        picture.data = img_response.content
                        
                        audio.clear_pictures()
                        audio.add_picture(picture)
                
                audio.save()
            except Exception as e:
                print(f"\nError adding metadata: {e}")

            print(f"{Fore.LIGHTGREEN_EX}\nDownloaded: {filename}")
            with lock:
                songs_downloaded += 1
            update_status()
            return True

        except requests.exceptions.HTTPError as e:
            print(f"{Fore.RED}\nHTTP Error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
        except Exception as e:
            print(f"{Fore.RED}\nAttempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            
        with lock:
            failed_downloads += 1
            errors.append(f"{song} - {artist}")
        return False


def generate_full_rgb_spectrum():
    gradient = []

    # Red to Yellow
    for i in range(256):
        gradient.append(f"#FF{hex(i)[2:].zfill(2)}00")

    # Yellow to Green
    for i in range(256):
        gradient.append(f"#{hex(255-i)[2:].zfill(2)}FF00")

    # Green to Cyan
    for i in range(256):
        gradient.append(f"#00FF{hex(i)[2:].zfill(2)}")

    # Cyan to Blue
    for i in range(256):
        gradient.append(f"#00{hex(255-i)[2:].zfill(2)}FF")

    # Blue to Magenta
    for i in range(256):
        gradient.append(f"#{hex(i)[2:].zfill(2)}00FF")

    # Magenta to Red
    for i in range(256):
        gradient.append(f"#FF00{hex(255-i)[2:].zfill(2)}")

    return gradient


class App:
    def __init__(self, root):
        self.playlist_path = ""
        self.download_directory = ""
        self.main_frame = ctk.CTkFrame(root, width=600, height=400)
        self.main_frame.pack(pady=20, padx=20, expand=True, fill=tk.BOTH)


        # Create Tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(expand=True, fill="both")

        # Create tabs
        self.playlist_tab = self.tabview.add("Playlist")
        self.search_tab = self.tabview.add("Search")

        # Playlist Tab
        self.setup_playlist_tab()
        
        # Search Tab
        self.setup_search_tab()

        self.rainbow_colors = generate_full_rgb_spectrum()
        self.current_color_index = 0
        self.update_rainbow_effect()

        self.discord_link = ctk.CTkLabel(
            self.main_frame,
            text="Join Our Discord",
            font=("Open Sans", 12),
            text_color="orange",
            cursor="hand2"
        )
        self.discord_link.pack(side="bottom", anchor="se", padx=10, pady=5)
        self.discord_link.bind("<Button-1>", lambda e: self.open_discord())

                # Add Help button
        self.help_button = ctk.CTkButton(
            self.main_frame,
            text="?",
            width=40,
            height=60,
            command=self.show_help,
            font=("Open Sans", 8, "bold")
        )
        self.help_button.pack(side="bottom", anchor="sw", padx=10, pady=5)

    def show_help(self):
        help_window = ctk.CTkToplevel()
        help_window.title("How to Use")
        help_window.geometry("400x200")
        
        # Center the window
        help_window.lift()
        help_window.grab_set()
        
        help_text = ("To use the playlist feature:\n\n"
                    "1. Go to TuneMyMusic.com\n\n"
                    "2. Export your playlist as a .txt file\n\n"
                    "3. Select the exported file using 'Select Playlist'")
        
        label = ctk.CTkLabel(
            help_window, 
            text=help_text,
            font=("Open Sans", 14),
            wraplength=350
        )
        label.pack(expand=True, padx=20, pady=20)

    def open_discord(self):
        import webbrowser
        webbrowser.open("https://discord.gg/sriracha")

    def setup_playlist_tab(self):
        max_width = 150
        vertical_padding = 20

        self.playlist_button = ctk.CTkButton(
            self.playlist_tab,
            text="Select Playlist",
            command=self.select_playlist,
            width=max_width,
        )
        self.playlist_button.pack(pady=vertical_padding)

        self.song_count_var = tk.StringVar(value="")
        self.song_count_label = ctk.CTkLabel(
            self.playlist_tab,
            textvariable=self.song_count_var,
            font=("Open Sans", 14))
        self.song_count_label.pack(pady=(0, vertical_padding))

        self.directory_button = ctk.CTkButton(
            self.playlist_tab,
            text="Select Download Directory",
            command=self.select_directory,
            width=max_width,
        )
        self.directory_button.pack(pady=vertical_padding)

        self.start_button = ctk.CTkButton(
            self.playlist_tab,
            text="Start Download",
            command=lambda: self.start_download('playlist'),
            width=max_width)
        self.start_button.pack(pady=vertical_padding)

    def setup_search_tab(self):
        max_width = 150
        vertical_padding = 20

        self.search_entry = ctk.CTkEntry(
            self.search_tab,
            placeholder_text="Artist - Song",
            width=300)
        self.search_entry.pack(pady=vertical_padding)

        self.search_dir_button = ctk.CTkButton(
            self.search_tab,
            text="Select Download Directory",
            command=self.select_directory,
            width=max_width,
        )
        self.search_dir_button.pack(pady=vertical_padding)

        self.search_button = ctk.CTkButton(
            self.search_tab,
            text="Download Song",
            command=lambda: self.start_download('search'),
            width=max_width)
        self.search_button.pack(pady=vertical_padding)

        self.status_label = ctk.CTkLabel(
            self.search_tab,
            text="",
            font=("Open Sans", 14))
        self.status_label.pack(pady=vertical_padding)

    def update_rainbow_effect(self):
        self.song_count_label.configure(
            text_color=self.rainbow_colors[self.current_color_index]
        )
        self.current_color_index = (self.current_color_index + 1) % len(
            self.rainbow_colors
        )
        self.song_count_label.after(4, self.update_rainbow_effect)

    def select_playlist(self):
        self.playlist_path = filedialog.askopenfilename()
        if self.playlist_path:
            with open(self.playlist_path, "r", encoding="utf-8-sig") as file:
                content = file.readlines()
                songs_count = sum(1 for line in content if " - " in line)
            self.song_count_var.set(f"Songs found: 🎵 {songs_count} 🎵")
            self.playlist_button.configure(
                text=f"Selected: {os.path.basename(self.playlist_path)}"
            )

    def select_directory(self):
        self.download_directory = filedialog.askdirectory().replace("/", "\\")
        if self.download_directory:
            self.directory_button.configure(
                text=f"Selected: {self.download_directory}")
            self.search_dir_button.configure(
                text=f"Selected: {self.download_directory}")

    def start_download(self, mode):
        if not self.download_directory:
            messagebox.showwarning(
                "Warning", "Please select a download directory.")
            return

        if mode == 'playlist':
            if not self.playlist_path:
                messagebox.showwarning("Warning", "Please select a playlist file.")
                return
            for _ in range(MAX_THREADS):
                threading.Thread(target=self.download_songs, daemon=True).start()
            self.process_playlist()
        else:  # search mode
            search_text = self.search_entry.get().strip()
            if not search_text or '-' not in search_text:
                messagebox.showwarning(
                    "Warning", "Please enter search in format: Artist - Song")
                return
            artist, song = search_text.split('-', 1)
            threading.Thread(
                target=lambda: self.download_single_song(
                    artist.strip(), song.strip()), 
                daemon=True
            ).start()

    def download_single_song(self, artist, song):
        global total_songs
        total_songs = 1
        
        try:
            # First get metadata
            service_url = "https://us.qobuz.squid.wtf"
            search_url = f"{service_url}/api/get-music?q={song}%20-%20{artist}&offset=0"
            response = requests.get(search_url, timeout=10)
            data = response.json()['data']
            
            tracks = []
            if 'most_popular' in data:
                most_popular_tracks = [item['content'] for item in data['most_popular'].get('items', [])
                                    if item.get('type') == 'tracks']
                tracks.extend(most_popular_tracks)
            
            if 'tracks' in data:
                tracks.extend(data['tracks'].get('items', []))

            if not tracks:
                raise ValueError("No tracks found")

            track = None
            for t in tracks:
                performer = t.get('performer', {}).get('name', '').lower()
                if performer == artist.lower():
                    track = t
                    break

            if track:
                # Get clean metadata
                real_artist = track.get('performer', {}).get('name', artist)
                real_title = track.get('title', song)
                # Remove any file system unsafe characters
                real_artist = re.sub(r'[<>:"/\\|?*]', '', real_artist)
                real_title = re.sub(r'[<>:"/\\|?*]', '', real_title)
                # Pass the clean names to download_song
                success = download_song(real_artist, real_title)
            else:
                success = download_song(artist, song)

            if success:
                self.status_label.configure(text="Download completed!")
            else:
                self.status_label.configure(text="Download failed.")
                
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
            print(f"Error in download_single_song: {str(e)}")

    def download_songs(self):
        while True:
            artist, song = download_queue.get()
            if artist is None and song is None:
                download_queue.task_done()
                break
            download_song(artist, song)
            download_queue.task_done()

    def process_playlist(self):
        global total_songs
        if not self.playlist_path:
            print("Playlist path not set.")
            return

        with open(self.playlist_path, "r", encoding="utf-8-sig") as file:
            content = file.readlines()
            songs_and_artists = [(line.split(" - ")[0].strip(), line.split(" - ")[1].strip())
                               for line in content if " - " in line]
            total_songs = len(songs_and_artists)

        for artist, song in songs_and_artists:
            download_queue.put((artist, song))

        for _ in range(MAX_THREADS):
            download_queue.put((None, None))


if __name__ == "__main__":
    init(autoreset=True)
    root = ctk.CTk()
    app = App(root)
    root.after(1000, app.update_rainbow_effect)
    root.title("Playlist to FLAC Downloader by Winters")

    window_width = 600
    window_height = 400
    root.geometry(f"{window_width}x{window_height}")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    root.geometry(f"+{x_position}+{y_position}")

    root.mainloop()

    # After GUI closes, process downloads
    errors = []
    failed_count = 0

    with open(app.playlist_path, "r", encoding="utf-8-sig") as file:
        content = file.readlines()
        songs_and_artists = [(line.split(" - ")[0].strip(), line.split(" - ")[1].strip())
                            for line in content if " - " in line]

    total_songs = len(songs_and_artists)
    
    # Create worker threads
    for _ in range(MAX_THREADS):
        threading.Thread(target=app.download_songs, daemon=True).start()

    # Queue songs
    for artist, song in songs_and_artists:
        download_queue.put((artist, song))

    # Wait for completion
    download_queue.join()

    # Write errors to file
    with open("download_errors.txt", "w") as f:
        for error in errors:
            song, artist = error.split(" - ")
            f.write(f"{artist} - {song}\n")

    print(f"{Fore.RED}Download errors for {len(errors)} songs. Details written to download_errors.txt.")
    print(f"{Fore.LIGHTGREEN_EX}All songs processed.", flush=True)
