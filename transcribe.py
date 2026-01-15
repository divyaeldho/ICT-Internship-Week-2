import whisper
import json
import os
from pydub import AudioSegment


# ---------------- CONFIG ----------------
AUDIO_PATH = "audio/extracted.wav"
CHUNK_FOLDER = "audio_chunks"
OUTPUT_PATH = "transcripts/transcript.json"

CHUNK_LENGTH_MS = 60 * 1000   # 60 seconds
# ---------------------------------------


def chunk_audio(audio_path, chunk_folder):
    audio = AudioSegment.from_wav(audio_path)
    os.makedirs(chunk_folder, exist_ok=True)

    chunks = []
    for i in range(0, len(audio), CHUNK_LENGTH_MS):
        chunk = audio[i:i + CHUNK_LENGTH_MS]
        chunk_path = f"{chunk_folder}/chunk_{i//1000}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append((chunk_path, i / 1000))  # (path, start_time)

    return chunks


def transcribe_chunks(chunks):
    print("Loading Whisper model (small)...")
    model = whisper.load_model("small")

    all_segments = []

    for chunk_path, offset in chunks:
        print(f"Transcribing {chunk_path} ...")

        result = model.transcribe(
            chunk_path,
            task="translate",
            language="en"
        )

        for seg in result["segments"]:
            seg["start"] += offset
            seg["end"] += offset
            all_segments.append(seg)

    return all_segments


def main():
    print("Chunking audio...")
    chunks = chunk_audio(AUDIO_PATH, CHUNK_FOLDER)

    print("Starting transcription...")
    segments = transcribe_chunks(chunks)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print("✅ Chunked transcription completed!")
    print(f"Transcript saved at: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
