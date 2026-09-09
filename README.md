# Khmer Audio → English Transcript

Simple Flask web app: upload a Khmer audio file, get back the Khmer transcript and an English translation, powered by the Gemini API (`gemini-3.6-flash`, multimodal audio understanding).

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

## 5. Using the app

1. Open http://127.0.0.1:5000 (run from inside the project folder, with the venv activated, as above).
2. Click the file picker and select a Khmer audio file from your computer (mp3, wav, m4a, aac, ogg, flac, or webm, up to 200MB).
3. Click **Transcribe**. The file is uploaded to Gemini's Files API and processed — this can take anywhere from a few seconds to a couple of minutes depending on audio length.
4. When it finishes, the page shows the Khmer transcript and the English translation side by side. Compare them against the audio to sanity-check the transcription.
5. If the result is marked truncated, the audio was long enough to hit the output token cap — see `MAX_OUTPUT_TOKENS`/`GENERATE_CONFIG` in `app.py` to raise it.

To stop the server, press `Ctrl+C` in the terminal where `python app.py` is running.

## Notes

- Max upload size is 200MB. Gemini itself supports much larger/longer audio via the Files API (used here), so this limit is just a sane app-level cap — raise `MAX_FILE_SIZE` in `app.py` if needed.
- The prompt asks for both a Khmer transcript and an English translation in one call, so you can sanity-check the transcription against the source audio.
- Uploaded files are stored in a temp file during processing and deleted afterward, both locally and from Gemini's Files API storage.
