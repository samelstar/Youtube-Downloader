import streamlit as st
import os
from yt_dlp import YoutubeDL

st.set_page_config(page_title="YouTube Playlist Downloader", layout="centered")
st.title("🎥 YouTube Playlist Downloader")
st.markdown("Download entire playlists as **MP4** or **MP3**.")

url = st.text_input("Playlist URL", placeholder="https://www.youtube.com/playlist?list=...")

col1, col2 = st.columns(2)
with col1:
    format_choice = st.radio("Output Format", ["MP4 (Video)", "MP3 (Audio)"], index=0)
with col2:
    quality = st.selectbox("Audio Quality (for MP3)", ["192 kbps", "128 kbps", "256 kbps"], index=0)

output_dir = "downloads"

if st.button("🚀 Start Download", type="primary"):
    if not url:
        st.error("Please enter a playlist URL.")
    else:
        with st.spinner("Downloading playlist... This may take a while for large playlists."):
            try:
                fmt = "mp3" if "MP3" in format_choice else "mp4"
                quality_kbps = quality.split()[0]

                ydl_opts = {
                    'outtmpl': f'{output_dir}/%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s',
                    'ignoreerrors': True,
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
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                        'merge_output_format': 'mp4',
                    })

                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                st.success("✅ Download completed!")
                st.info(f"Files saved in `./{output_dir}` folder (relative to the app).")

                # Optional: List downloaded files
                if os.path.exists(output_dir):
                    st.subheader("Downloaded Playlists")
                    for item in os.listdir(output_dir):
                        st.write(f"📁 {item}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.caption("Built with yt-dlp + Streamlit • For personal use only. Respect YouTube's terms.")