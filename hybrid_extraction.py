import json
import subprocess
import os
import re

from sentence_transformers import SentenceTransformer, util


# ---------------- Configuration ----------------
TRANSCRIPT_PATH = "transcripts/transcript.json"
VIDEO_PATH = "video/source_video.webm"

BUFFER_SECONDS = 15
OUTPUT_DURATION = 60


# ---------------- NLP Models ----------------
print("Loading semantic model...")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------- Keyword Definitions ----------------
QUESTION_KEYWORDS = [
    "what", "why", "how", "when", "where",
    "who", "which", "can you", "could you",
    "do you", "is it", "are you"
]

AGREEMENT_KEYWORDS = [
    "i agree",
    "yes",
    "right",
    "correct",
    "exactly",
    "true",
    "makes sense",
    "i think so"
]

DISAGREEMENT_KEYWORDS = [
    "i disagree",
    "no",
    "not correct",
    "not true",
    "wrong",
    "i dont think so"
]


# ---------------- Semantic Intent Templates ----------------
INTENT_TEMPLATES = {
    "agreement": [
        "I agree with that",
        "That is correct",
        "Yes, absolutely",
        "That makes sense"
    ],
    "disagreement": [
        "I disagree with that",
        "That is wrong",
        "I do not agree",
        "That is not correct"
    ]
}



def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def load_transcript(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_output_folders():
    os.makedirs("outputs/question_answer", exist_ok=True)
    os.makedirs("outputs/agreement", exist_ok=True)
    os.makedirs("outputs/disagreement", exist_ok=True)


def extract_video_output(start_time, category, index):
    output_start_time = max(0, start_time - BUFFER_SECONDS)
    output_path = f"outputs/{category}/{category}_{index}.mp4"

    ffmpeg_command = [
        "ffmpeg", "-y",
        "-ss", str(output_start_time),
        "-i", VIDEO_PATH,
        "-t", str(OUTPUT_DURATION),
        "-c:v", "libx264",
        "-c:a", "aac",
        output_path
    ]

    subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def semantic_score(text, intent):
    texts = [text] + INTENT_TEMPLATES[intent]
    embeddings = semantic_model.encode(texts)
    sentence_emb = embeddings[0]
    intent_embs = embeddings[1:]

    scores = util.cos_sim(sentence_emb, intent_embs)
    return float(scores.max())


# ---------------- Main Processing ----------------
print("Loading transcript...")
segments = load_transcript(TRANSCRIPT_PATH)

create_output_folders()

qa_count = 1
agreement_count = 1
disagreement_count = 1

print("Detecting moments using HYBRID logic...")

for i, segment in enumerate(segments):
    raw_text = segment["text"]
    cleaned_text = clean_text(raw_text)
    start_time = segment["start"]

    # -------- Question Detection (Rule-based) --------
    is_question = any(q in cleaned_text for q in QUESTION_KEYWORDS)

    if is_question:
        extract_video_output(start_time, "question_answer", qa_count)
        qa_count += 1

        # -------- Conversation Structure: Answer Detection --------
        if i + 1 < len(segments):
            next_segment = segments[i + 1]
            time_gap = next_segment["start"] - segment["end"]

            if time_gap < 2.5:
                extract_video_output(
                    next_segment["start"],
                    "question_answer",
                    qa_count
                )
                qa_count += 1
        continue

    # -------- Agreement Detection (Hybrid) --------
    rule_agree = any(w in cleaned_text for w in AGREEMENT_KEYWORDS)
    semantic_agree = semantic_score(cleaned_text, "agreement")

    agreement_score = (0.6 * int(rule_agree)) + (0.4 * semantic_agree)

    if agreement_score > 0.6:
        extract_video_output(start_time, "agreement", agreement_count)
        agreement_count += 1
        continue

    # -------- Disagreement Detection (Hybrid) --------
    rule_disagree = any(w in cleaned_text for w in DISAGREEMENT_KEYWORDS)
    semantic_disagree = semantic_score(cleaned_text, "disagreement")

    disagreement_score = (0.6 * int(rule_disagree)) + (0.4 * semantic_disagree)

    if disagreement_score > 0.6:
        extract_video_output(start_time, "disagreement", disagreement_count)
        disagreement_count += 1


print("✅ Hybrid AI moment extraction completed successfully!")
