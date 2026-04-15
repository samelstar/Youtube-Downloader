import os
import sys
from yt_dlp import YoutubeDL

def download_playlist(playlist_url, format_choice="mp4", output_dir="downloads"):
    """
    Download a YouTube playlist as MP4 or MP3.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Common options
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s',
        'ignoreerrors': True,
        'no_warnings': False,
        'quiet': False,
    }

    if format_choice.lower() == "mp3":
        # Audio only → MP3 with best quality
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',  # You can change to 128, 256, etc.
            }],
            'postprocessor_args': [
                '-metadata', 'album=%(playlist_title)s',
            ],
        })
        print("Downloading playlist as MP3 (audio only)...")
    else:
        # Video as MP4 (best quality)
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })
        print("Downloading playlist as MP4 (video + audio)...")

    with YoutubeDL(ydl_opts) as ydl:
        print(f"Starting download from: {playlist_url}")
        ydl.download([playlist_url])

    print(f"\nDownload complete! Files saved in: ./{output_dir}")

if __name__ == "__main__":
    print("=== YouTube Playlist Downloader ===\n")
    
    url = input("Enter YouTube playlist URL: ").strip()
    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    fmt = input("Choose format (mp4 or mp3) [default: mp4]: ").strip().lower()
    if fmt not in ["mp4", "mp3"]:
        fmt = "mp4"
        print("Invalid choice. Defaulting to mp4.")

    download_playlist(url, format_choice=fmt)