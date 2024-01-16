# Playlist to FLAC Downloader / Converter

This Python script allows you to download songs from a playlist in Lossless FLAC format using Selenium and the CapSolver API to automate the solving of CAPTCHAs.

![alt text](https://files.catbox.moe/gzo64v.png)

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Exporting a Playlist from TuneMyMusic](#exporting-a-playlist-from-tunemymusic)
- [Getting a CapSolver API Key](#getting-a-capsolver-api-key)
- [Contributing](#contributing)
- [License](#license)

## Requirements

Before using this script, make sure you have the following requirements installed:
- Python 3.x
- Selenium
- Requests
- CustomTkinter
- Colorama
- Mozilla Firefox (GeckoDriver)

## Installation

You can install the required Python modules using the following command:

```bash
pip install selenium requests customtkinter colorama
```

Make sure you have Mozilla Firefox installed and download the [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for your specific platform. Add the path to the GeckoDriver executable to your system's PATH environment variable.

## Usage

1. Run the script using Python:

```bash
python flacdownloader.py
```

2. The script will open a graphical user interface (GUI) using CustomTkinter.

3. Follow these steps within the GUI:
   - Click "Select Playlist" to choose your playlist file. The script expects a text file with each line in the format "Artist - Song Title".
   - Click "Select Download Directory" to choose where you want to save the downloaded songs.
   - Enter your CapSolver API Key in the "CapSolver API Key" field. You can get a CapSolver API Key from [CapSolver](https://capsolver.com/).
   - Click "Start" to begin the download process.

4. The script will automate the process of searching for each song, solving CAPTCHAs if required, and downloading them in FLAC format.

5. Progress and errors will be displayed in the console.

6. Download errors will be saved in a file named `download_errors.txt` for your reference.

## Exporting a Playlist from TuneMyMusic

To use this script, you need a playlist file in the format "Artist - Song Title". If you sync a playlist to TuneMyMusic and export that playlist as a .txt (FREE), the format will be what you need:

1. Visit [TuneMyMusic](https://www.tunemymusic.com/).

2. Select the source platform where your playlist is located (e.g., Spotify, YouTube, Apple Music).

3. Follow the on-screen instructions to import your playlist from the source platform.

4. Once your playlist is imported, you can see it on the TuneMyMusic platform.

5. Look for an option to export the playlist. It's usually labeled as "Export," "Save," or "Download."

6. Choose the export format as plain text (.txt), which will give you a file with the "Artist - Song Title" format.

7. Save the exported playlist file to your computer.

Now, you can use this exported playlist file with the script.

## Getting a CapSolver API Key

To use CapSolver for solving CAPTCHAs with this script, you'll need a CapSolver account and an API Key. Here's how to get it:

1. Visit [CapSolver](https://capsolver.com/) and create an account if you don't already have one.

2. Log in to your CapSolver account.

3. Once logged in, you can find your API Key in your account settings or dashboard. Copy the API Key.

4. Make sure to add money to your CapSolver account to cover the costs of solving CAPTCHAs. You can usually do this by following the instructions on the CapSolver website.

5. Paste your API Key into the "CapSolver API Key" field in the script's GUI.

> [!NOTE]
> Currently, the rate for solving reCAPTCHAV2 is $0.8 / 1000 solves.
> If you want to use the project but do not have the ability to add money to a CapSolver account, feel free to message me on [Discord](https://discordapp.com/users/681989594341834765) and I will sponsor your session for a star (:

Now, you're ready to use CapSolver with the script to automatically solve CAPTCHAs during the download process.

## Contributing

If you want to contribute to this project, feel free to fork the repository and submit a pull request with your improvements. Please ensure that your code is well-documented and follows best practices.

## License

This project is licensed under the [MIT License](LICENSE).
