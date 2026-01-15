import yt_dlp


def extract_audio_from_youtube(video_url, output_path="audio/extracted"):
    """
    Extracts high-quality audio from a YouTube video
    and saves it in WAV format.
    """

    print("Starting audio extraction...")

    ydl_options = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_path}.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_options) as downloader:
            downloader.download([video_url])

        print("Audio extracted and saved successfully!")

    except Exception as error:
        print("Audio extraction failed.")
        print(f"Error details: {error}")


# ---- Script execution ----
YOUTUBE_URL = "https://youtu.be/u3CT3pl7Cik?si=3_W7aV0YHkrQ0t31"

extract_audio_from_youtube(YOUTUBE_URL)