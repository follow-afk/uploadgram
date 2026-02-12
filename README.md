# UploadGram (Optimized)

UploadGram is a high-performance CLI tool that uses your Telegram account to upload files up to 4 GiB (for Premium users) or 2 GiB (for standard users) directly from the terminal.

This version has been optimized for **increased upload speeds** and **modernized** to work with the latest Python versions and Telegram API features.

## Key Improvements

- **Faster Uploads**: Increased concurrent transmissions and optimized worker settings.
- **Modernized Core**: Updated to use the latest `pyrogram` v2.x and Python 3.10+.
- **Efficient Progress**: Optimized UI updates to reduce API overhead and latency.
- **Smart Seek**: Faster thumbnail generation using optimized FFmpeg seeking.
- **Better Stability**: Improved error handling and dependency management.

## Installation

```sh
pip install uploadgram
```

## Requirements

- Python 3.10 or higher
- `ffmpeg` (for video thumbnail generation)
- Telegram API credentials (`api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org))

## Usage

```sh
# Basic usage
uploadgram <chat_id> <file_or_directory_path>

# Advanced usage
uploadgram <chat_id> /path/to/files --delete_on_success --fd --progress --caption "My Upload" --topic 123
```

### Options

- `chat_id`: Target chat ID, username, or phone number.
- `dir_path`: Path to the file or directory you want to upload.
- `--delete_on_success`: Delete the local file after a successful upload.
- `--fd`: Force upload as a document (skips video/audio processing).
- `--t`: Path to a custom thumbnail image.
- `--caption`: Set a custom caption for the uploaded files.
- `--progress`: Show a real-time progress bar in the terminal.
- `--topic`: Upload to a specific forum topic (thread ID).

## Credits

- Heavily inspired by [telegram-upload](https://github.com/Nekmo/telegram-upload)
- Powered by [Pyrogram](https://github.com/pyrogram/pyrogram)
