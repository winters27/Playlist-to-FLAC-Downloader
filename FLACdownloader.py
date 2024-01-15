import os
import sys
import time
import subprocess
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from tkinter import filedialog, messagebox
import customtkinter as ctk
import tkinter as tk
from colorama import Fore, Back, Style, init
import json

# Constants
MAX_WAIT_TIME = 25  # seconds

def install_required_modules():
    required_modules = [
        "selenium", 
        "requests", 
        "customtkinter", 
        "tkinter", 
        "colorama", 
        "datetime", 
        "json"
    ]
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])

init(autoreset=True)

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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App:
    def __init__(self, root):
        self.playlist_path = ""
        self.download_directory = ""
        self.api_key = tk.StringVar()
        self.driver = None

        self.main_frame = ctk.CTkFrame(root, width=600, height=400)
        self.main_frame.pack(pady=20, padx=20, expand=True, fill=tk.BOTH)

        # Define max width for the widgets
        max_width = 150
        vertical_padding = 20

        # Create the UI elements using customtkinter
        self.playlist_button = ctk.CTkButton(self.main_frame, text="Select Playlist", command=self.select_playlist, width=max_width)
        self.playlist_button.grid(row=0, column=0, columnspan=1, pady=vertical_padding, sticky='n')

        # Label for "Songs found:"
        self.static_label = ctk.CTkLabel(self.main_frame, text="", font=("Open Sans", 14))
        self.static_label.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky='e')

        # Label to display the song count with rainbow effect
        self.song_count_var = tk.StringVar(value="")
        self.song_count_label = ctk.CTkLabel(self.main_frame, textvariable=self.song_count_var, font=("Open Sans", 14))
        self.song_count_label.grid(row=1, column=0, pady=(10, 0), sticky='n')  # Centered in the grid


        self.directory_button = ctk.CTkButton(self.main_frame, text="Select Download Directory", command=self.select_directory, width=max_width)
        self.directory_button.grid(row=2, column=0, pady=20, sticky='n')

        self.api_entry_label = ctk.CTkLabel(self.main_frame, text="CapSolver API Key:")
        self.api_entry_label.grid(row=3, column=0, pady=0, sticky='n')

        self.api_entry = ctk.CTkEntry(self.main_frame, textvariable=self.api_key, font=("Open Sans", 18), width=400)
        self.api_entry.grid(row=4, column=0, pady=0, sticky='n')

        self.start_button = ctk.CTkButton(self.main_frame, text="Start", command=self.start_download, width=max_width)
        self.start_button.grid(row=5, column=0, pady=vertical_padding, sticky='n')

        # Adjust column and row weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # For playlist_button
        self.main_frame.rowconfigure(1, weight=0)  # For song_count_label (minimal spacing)
        self.main_frame.rowconfigure(2, weight=2)  # For directory_button
        self.main_frame.rowconfigure(3, weight=1)  # For api_entry_label and api_entry
        self.main_frame.rowconfigure(4, weight=1)  # For start_button

        # Initialize the rainbow effect on the song count label
        self.rainbow_colors = generate_full_rgb_spectrum()
        self.current_color_index = 0
        self.update_rainbow_effect()

    def update_rainbow_effect(self):
        """Updates song count color with a dynamic rainbow effect."""
        self.song_count_label.configure(text_color=self.rainbow_colors[self.current_color_index])
        self.current_color_index = (self.current_color_index + 1) % len(self.rainbow_colors)
        self.song_count_label.after(4, self.update_rainbow_effect)  # Change color every 300 milliseconds

    def set_song_count(self, count):
        """Updates the song count label."""
        self.song_count_var.set(count)


    def select_playlist(self):
        self.playlist_path = filedialog.askopenfilename()
        if self.playlist_path:
            with open(self.playlist_path, 'r', encoding='utf-8-sig') as file:
                content = file.readlines()
                songs_count = sum(1 for line in content if ' - ' in line)
            self.song_count_var.set(f"Songs found: 🎵 {songs_count} 🎵")
            self.playlist_button.configure(text=f"Selected: {os.path.basename(self.playlist_path)}")

    def select_directory(self):
        self.download_directory = filedialog.askdirectory().replace("/", "\\")
        if self.download_directory:
            self.directory_button.configure(text=f"Selected: {self.download_directory}")

    def start_download(self):
        global CAPSOLVER_API_KEY
        CAPSOLVER_API_KEY = self.api_key.get()
        global options

        if not self.playlist_path or not self.download_directory or not self.api_key.get():
            messagebox.showwarning("Warning", "Please provide all necessary information before starting.")
            return

        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/flac")
        options.set_preference("browser.download.dir", self.download_directory)
        print(f"Setting download directory to: {self.download_directory}")
        options.set_preference("browser.download.useDownloadDir", True)

        self.driver = webdriver.Firefox(options=options)


        # You can now start the download process and close the UI
        root.destroy()


root = ctk.CTk()
app = App(root)
root.after(1000, app.update_rainbow_effect)  # Start the animation
root.title("Playlist to FLAC Downloader")


# Set window size
window_width = 600  # You can adjust this value
window_height = 400  # You can adjust this value
root.geometry(f"{window_width}x{window_height}")

# Center the window on the screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = int((screen_width - window_width) / 2)
y_position = int((screen_height - window_height) / 2)
root.geometry(f"+{x_position}+{y_position}")

root.mainloop()


errors = []
failed_count = 0

def is_download_active(directory):
    for filename in os.listdir(directory):
        if filename.endswith(('.part', '.crdownload', '.tmp')):
            return True
    return False

def download_song(driver, artist, song):
    global failed_count
    start_time = datetime.now()

    headers = {"Content-Type": "application/json"}

    # Navigate to the site
    driver.get("https://free-mp3-download.net/")
    try:
        search_box = driver.find_element(By.CSS_SELECTOR, "#q")
        search_box.clear()
        search_box.send_keys(f"{song} - {artist}")
        search_box.send_keys(Keys.RETURN)
        print(Fore.LIGHTYELLOW_EX + "Searching...\n")

        # Wait for the search results to load
        download_btn = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#results_t > tr:nth-child(1) > td:nth-child(3) > a:nth-child(1) > button:nth-child(1)"))
        )

        # Scroll to the button and click it
        driver.execute_script("arguments[0].scrollIntoView();", download_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", download_btn)
        print(Fore.LIGHTYELLOW_EX + "Song Found...\n")

        # Select the FLAC radio button
        flac_radio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.col:nth-child(3) > p:nth-child(1) > label:nth-child(2)"))
        )
        flac_radio.click()
        print(Fore.LIGHTYELLOW_EX + "Finding Lossless/FLAC format...\n")

        # Check for the presence of CAPTCHA by looking for the reCAPTCHA iframe
        try:
            captcha_frame = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'https://www.google.com/recaptcha/api2/anchor')]"))
            )
            captcha_present = True
        except TimeoutException:
            captcha_present = False

        # If CAPTCHA is present, solve it
        if captcha_present:
            # Solve the CAPTCHA using CapSolver
            site_key = "6LfzIW4UAAAAAM_JBVmQuuOAw4QEA1MfXVZuiO2A"
            url = driver.current_url
            payload = {
                "clientKey": CAPSOLVER_API_KEY,
                "task": {
                    "type": "ReCaptchaV2Task",
                    "websiteURL": url,
                    "websiteKey": site_key,
                }
            }
            response = requests.post("https://api.capsolver.com/createTask", json=payload)
            response_data = response.json()

            if response_data.get("errorId") == 0:
                task_id = response_data.get("taskId")
                # Wait for the solution
                while True:
                    solution_response = requests.post("https://api.capsolver.com/getTaskResult", json={
                        "clientKey": CAPSOLVER_API_KEY,
                        "taskId": task_id
                    })
                    solution_data = solution_response.json()
                    if solution_data.get("status") == "ready":
                        break
                    time.sleep(5)

                # Input the solution into the CAPTCHA form
                recaptcha_solution = solution_data.get("solution", {}).get("gRecaptchaResponse")
                if recaptcha_solution:
                    driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML='{recaptcha_solution}';")
                    print(Fore.LIGHTGREEN_EX + "CAPTCHA solved!\n")

        # Click the final download button 
        final_download_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".dl"))
        )
        final_download_btn.click()
        print(Fore.LIGHTYELLOW_EX + "Attempting to Download...\n")

        # Wait for the download to start
        download_start_time = time.time()
        download_directory = app.download_directory
        while not is_download_active(download_directory) and time.time() - download_start_time < MAX_WAIT_TIME:
            print(Fore.LIGHTYELLOW_EX + "Checking for active download...\n")
            time.sleep(1)

        if time.time() - download_start_time >= MAX_WAIT_TIME:
            print(Fore.RED + f"Download for '{song} - {artist}' did not start in the expected time. Skipping...")
            errors.append(f"{song} - {artist}")
            failed_count += 1
            return

        print(Fore.LIGHTYELLOW_EX + "Download started...\n")

        # Wait for the download to finish
        download_completion_time = time.time()
        while is_download_active(download_directory) and time.time() - download_completion_time < MAX_WAIT_TIME:
            print(Fore.LIGHTYELLOW_EX + "Waiting for the download to finish...\n")
            time.sleep(5)

        if time.time() - download_completion_time >= MAX_WAIT_TIME:
            print(Fore.RED + f"Download for '{song} - {artist}' did not finish in the expected time. Skipping...")
            errors.append(f"{song} - {artist}")
            failed_count += 1
            return

        print(Fore.LIGHTGREEN_EX + "Download Success!")
        time.sleep(1)

    except TimeoutException:
        print(f"Timeout error for {song} - {artist}")
        failed_count += 1
    except NoSuchElementException:
        print(f"Element not found error for {song} - {artist}")
        failed_count += 1
    except ElementNotInteractableException:
        print(f"Element not interactable error for {song} - {artist}")
        failed_count += 1
    except Exception as e:
        print(f"General error for {song} - {artist}: {str(e)}")
        failed_count += 1

    # Return the elapsed time for the song download
    return (datetime.now() - start_time).seconds

# Extract the songs and artists from the file
with open(app.playlist_path, 'r', encoding='utf-8-sig') as file:
    content = file.readlines()
    songs_and_artists = [(line.split(' - ')[0].strip(), line.split(' - ')[1].strip()) for line in content if ' - ' in line]

def format_time(seconds):
    """Format time to be readable, converting to hours/minutes/seconds when appropriate."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours} hours {minutes} minutes"
    else:
        return f"{minutes} minutes"

total_time_taken = 0
for idx, (artist, song) in enumerate(songs_and_artists):
    start_time = time.time()
    
    print(Fore.LIGHTGREEN_EX + f"\nProcessing {Fore.LIGHTGREEN_EX}{idx + 1}/{len(songs_and_artists)}{Fore.RESET}: {Fore.CYAN}{song} by {artist}{Fore.RESET}", flush=True)

    download_song(app.driver, artist, song)
    
    elapsed_time = time.time() - start_time
    total_time_taken += elapsed_time
    
    average_time_per_song = total_time_taken / (idx + 1)
    estimated_remaining_time = average_time_per_song * (len(songs_and_artists) - idx - 1)
    
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the terminal
    print(Fore.WHITE + Back.BLUE + f"Download ETA: {format_time(estimated_remaining_time)} " + Fore.RESET + Back.RESET + " | " + Fore.WHITE + Back.RED + f" Failed Downloads: {failed_count} {Fore.RESET + Back.RESET}", flush=True)



with open('download_errors.txt', 'w') as f:
    for error in errors:
        song, artist = error.split(' - ')
        f.write(f"{artist} - {song}\n")


print(Fore.RED + f"Download errors for {len(errors)} songs. Details written to download_errors.txt.")

app.driver.quit()

print(Fore.LIGHTGREEN_EX + "All songs processed.", flush=True)
