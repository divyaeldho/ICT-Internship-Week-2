# AI Moment Extraction System

This project implements a hybrid AI-based system to automatically extract meaningful moments
(question-answer, agreement, disagreement) from videos.

## Features
- YouTube video & audio download
- Whisper-based multilingual transcription with audio chunking
- Hybrid moment detection:
  - Rule-based keywords
  - Semantic similarity
  - Conversational structure
- Automatic video clip extraction using FFmpeg

## Tech Stack
- Python
- Whisper
- Sentence Transformers
- FFmpeg
- yt-dlp

## Workflow
1. Download video & audio
2. Transcribe audio using Whisper (chunked)
3. Detect conversational moments (hybrid approach)
4. Extract corresponding video clips

## Note
Generated files (audio, video, outputs) are ignored from version control.
