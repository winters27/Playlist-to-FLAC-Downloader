# Playlist to FLAC Downloader / Converter

This Python script allows you to download songs from a playlist in Lossless FLAC format. Features a modern, janky GUI with playlist and search functionality.

![alt text](https://files.catbox.moe/9i2qi9.png)

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Exporting a Playlist from TuneMyMusic](#exporting-a-playlist-from-tunemymusic)
- [Contributing](#contributing)
- [License](#license)

## Requirements

Before using this script, make sure you have the following requirements installed:
- Python 3.x
- Requests
- CustomTkinter
- Colorama

## Installation

You can install the required Python modules using the following command:

```bash
pip install requests customtkinter colorama
```

## Usage

> [!CAUTION]
> This script utilizes multi-threading to enhance performance and efficiency, especially when handling multiple downloads simultaneously. It's important to be aware of how threading is used and how it can be adjusted to suit your needs and system capabilities.

### Thread Count: 
The script currently sets a maximum number of threads (MAX_THREADS) which determines how many download processes can run concurrently. While a higher number of threads can increase download speed, it also increases the load on your system which can lead to performance issues or instability, especially on computers with limited resources.

### Modifying Thread Count:
If you find that the script is running slowly or causing system instability, consider reducing the number of threads. Conversely, if you have a powerful machine and want to increase download speeds, you may increase the thread count. This setting is found in the MAX_THREADS constant at the top of the script.
```bash
MAX_THREADS = 5  # Example: Change this number to increase or decrease threads
```

### Run the Script

1. Run the script using Python:

```bash
python flacdownloader.py
```

2. The script will open a graphical user interface (GUI) using CustomTkinter.

## Playlist Tab

- Click "Select Playlist" to choose your playlist file
- Select download directory
- Click "Start Download" to begin

## Search Tab

- Enter song in "Artist - Song" format
- Select download directory
- Click "Download Song"

3. The script will automate the process of searching for each song.

4. Progress and errors will be displayed in the console.

5. Download errors will be saved in a file named `download_errors.txt` for your reference.

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


## Contributing

If you want to contribute to this project, feel free to fork the repository and submit a pull request with your improvements. Please ensure that your code is well-documented and follows best practices.

## License

This project is licensed under the [MIT License](LICENSE).
