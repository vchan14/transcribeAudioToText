# Khmer Audio → English Transcript

Simple Flask web app: upload a Khmer audio file, get back the Khmer transcript and an English translation, powered by the Gemini API (`gemini-2.5-flash`, multimodal audio understanding).

## 1. Get a Gemini API key

1. Go to https://aistudio.google.com/apikey
2. Sign in with a Google account and click "Create API key" (a free tier is available).
3. Copy the key.

## 2. Configure

```bash
cp .env.example .env
```

Edit `.env` and paste your key:

```
GEMINI_API_KEY=AIza...
```

## 3. Install dependencies

A `.venv` already exists in this folder. Activate it and install requirements:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Run

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser, choose an audio file (mp3, wav, m4a, aac, ogg, flac, webm), and click Transcribe.

## Notes

- Max upload size is 200MB. Gemini itself supports much larger/longer audio via the Files API (used here), so this limit is just a sane app-level cap — raise `MAX_FILE_SIZE` in `app.py` if needed.
- The prompt asks for both a Khmer transcript and an English translation in one call, so you can sanity-check the transcription against the source audio.
- Uploaded files are stored in a temp file during processing and deleted afterward, both locally and from Gemini's Files API storage.
