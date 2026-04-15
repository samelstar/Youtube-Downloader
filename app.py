import streamlit as st
import tempfile
import zipfile
import os
from yt_dlp import YoutubeDL
from pathlib import Path

st.set_page_config(page_title="YouTube Playlist Downloader", layout="centered")
st.title("🎥 YouTube Playlist Downloader")
st.markdown("Download playlists as **MP4** or **MP3**. (Updated April 2026 to handle YouTube changes)")

url = st.text_input("Playlist URL", placeholder="https://www.youtube.com/playlist?list=...")

col1, col2 = st.columns(2)
with col1:
    format_choice = st.radio("Output Format", ["MP4 (Video)", "MP3 (Audio)"], index=0)
with col2:
    quality = st.selectbox("MP3 Quality", ["192 kbps", "128 kbps", "256 kbps"], index=0)

if st.button("🚀 Start Download", type="primary"):
    if not url:
        st.error("Please enter a playlist URL.")
    else:
        with st.spinner("Downloading... This may take time for large playlists."):
            try:
                with tempfile.TemporaryDirectory() as tmp_dir:
                    download_path = Path(tmp_dir)
                    
                    fmt = "mp3" if "MP3" in format_choice else "mp4"
                    quality_kbps = quality.split()[0]

                    ydl_opts = {
                        'outtmpl': str(download_path / '%(playlist_title)s - %(playlist_index)02d - %(title)s.%(ext)s'),
                        'ignoreerrors': True,
                        'quiet': False,
                        # Key fixes for 403 errors in 2026:
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['web', 'web_embedded', 'tv'], # Avoid problematic android clients
                                # 'po_token': '...' # Advanced: add if needed later
                            }
                        },
                        # Additional helpful options
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
                        },
                        'retries': 5,
                        'fragment_retries': 5,
                    }

                    if fmt == "mp3":
                        ydl_opts.update({
                            'format': 'bestaudio/best',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': quality_kbps,
                            }],
                        })
                    else:
                        # Prefer combined formats when possible to reduce 403 risk
                        ydl_opts.update({
                            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                            'merge_output_format': 'mp4',
                        })

                    st.info("Starting download with updated YouTube settings...")
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)

                    # Collect downloaded files
                    downloaded_files = list(download_path.rglob("*.*"))
                    if not downloaded_files:
                        st.error("No files downloaded. The playlist may be private, age-restricted, or currently blocked by YouTube.")
                        st.stop()

                    # Create ZIP
                    zip_path = download_path / "playlist.zip"
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for file in downloaded_files:
                            if file.is_file():
                                arcname = file.relative_to(download_path)
                                zipf.write(file, arcname)

                    with open(zip_path, "rb") as f:
                        zip_bytes = f.read()

                    playlist_name = info.get('title', 'YouTube_Playlist') if isinstance(info, dict) else 'YouTube_Playlist'

                    st.success("✅ Download completed! ZIP is ready.")
                    st.download_button(
                        label="📥 Download Playlist as ZIP",
                        data=zip_bytes,
                        file_name=f"{playlist_name}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

                    with st.expander("📋 Downloaded files"):
                        for f in downloaded_files:
                            size_mb = f.stat().st_size / (1024 * 1024)
                            st.write(f"• {f.name} ({size_mb:.1f} MB)")

            except Exception as e:
                st.error(f"Download error: {str(e)}")
                st.info("Tips:\n• Try a smaller/public playlist\n• YouTube changes often — try again later\n• For best results, use the desktop Python script locally")
