import os
import tempfile

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set. "
        "Copy .env.example to .env and add your key."
    )

client = genai.Client(api_key=API_KEY)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB

PROMPT = """You are given an audio recording in Khmer.

Transcribe the ENTIRE recording from start to finish, word for word, in
continuous Khmer script. Do not summarize, do not skip repeated or filler
speech, and do not stop early — keep going until you reach the very end of
the audio, no matter how long it is. Then translate that full transcript
into natural, fluent English, covering the same content start to finish.

Respond in exactly this format, with no extra commentary:

KHMER:
<full khmer transcript, start to finish>

ENGLISH:
<full english translation, start to finish>
"""

GENERATE_CONFIG = types.GenerateContentConfig(
    max_output_tokens=65536,
    thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    ext = os.path.splitext(audio_file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file type: {ext}"}), 400

    tmp_path = None
    uploaded_name = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name

        uploaded = client.files.upload(file=tmp_path)
        uploaded_name = uploaded.name

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[uploaded, PROMPT],
            config=GENERATE_CONFIG,
        )
        khmer, english = parse_response(response.text or "")

        truncated = False
        if response.candidates:
            truncated = response.candidates[0].finish_reason == types.FinishReason.MAX_TOKENS

        usage = response.usage_metadata
        token_usage = {
            "prompt_tokens": usage.prompt_token_count,
            "thoughts_tokens": usage.thoughts_token_count,
            "output_tokens": usage.candidates_token_count,
            "total_tokens": usage.total_token_count,
        } if usage else None

        return jsonify({
            "khmer": khmer,
            "english": english,
            "truncated": truncated,
            "token_usage": token_usage,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        if uploaded_name:
            try:
                client.files.delete(name=uploaded_name)
            except Exception:
                pass


def parse_response(text):
    if "KHMER:" in text and "ENGLISH:" in text:
        khmer = text.split("KHMER:", 1)[1].split("ENGLISH:", 1)[0].strip()
        english = text.split("ENGLISH:", 1)[1].strip()
        return khmer, english
    return "", text.strip()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
