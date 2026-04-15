import streamlit as st
import os
import shutil
import tempfile
import zipfile
from yt_dlp import YoutubeDL
from pathlib import Path

st.set_page_config(page_title="YouTube Playlist Downloader", layout="centered")
st.title("🎥 YouTube Playlist Downloader")
st.markdown("Download entire playlists as **MP4** or **MP3** and save them directly to your device.")

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
        with st.spinner("Downloading playlist... (this can take several minutes for large playlists)"):
            try:
                # Create a unique temporary directory for this download
                with tempfile.TemporaryDirectory() as tmp_dir:
                    download_path = Path(tmp_dir)
                    
                    fmt = "mp3" if "MP3" in format_choice else "mp4"
                    quality_kbps = quality.split()[0]

                    ydl_opts = {
                        'outtmpl': str(download_path / '%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s'),
                        'ignoreerrors': True,
                        'quiet': False,
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
                        ydl_opts.update({
                            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                            'merge_output_format': 'mp4',
                        })

                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                    # Find the playlist folder inside tmp_dir
                    playlist_folders = [f for f in download_path.iterdir() if f.is_dir()]
                    if not playlist_folders:
                        st.error("No files were downloaded.")
                        st.stop()
                    
                    playlist_folder = playlist_folders[0] # Usually only one playlist folder

                    # Create zip file in memory or on disk
                    zip_path = download_path / "playlist_download.zip"
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, dirs, files in os.walk(playlist_folder):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(playlist_folder.parent)
                                zipf.write(file_path, arcname)

                    # Read the zip for download button
                    with open(zip_path, "rb") as f:
                        zip_bytes = f.read()

                    st.success("✅ Download ready!")
                    st.download_button(
                        label="📥 Download Playlist as ZIP",
                        data=zip_bytes,
                        file_name=f"{playlist_folder.name}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

                    # Optional: Show list of files inside
                    with st.expander("View downloaded files"):
                        for file in playlist_folder.rglob("*"):
                            if file.is_file():
                                st.write(f"• {file.relative_to(playlist_folder)}")

            except Exception as e:
                st.error(f"Error during download: {str(e)}")
                st.info("Tip: Try a smaller playlist or check if the URL is public.")
