from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
import fitz

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

def get_summary(text):
    prompt = f"""
    You are an expert academic summarizer.
    Summarize the following content clearly and concisely.
    Use bullet points where helpful.

    Content:
    {text}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text



@app.route('/summarize/text', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text = data['text']
    prompt = f"Summarize the following text:\n{text}"
    summary = get_summary(prompt)
    return jsonify({'summary': summary})

@app.route('/summarize/pdf', methods=['POST']) 
def summarize_pdf():
    file = request.files['file']
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    prompt = f"Summarize the following PDF content:\n{text}"
    summary = get_summary(prompt)
    return jsonify({'summary': summary})   

@app.route('/summarize/youtube', methods=['POST'])
def summarize_youtube():
    data = request.get_json()
    url = data['url']
    video_id = url.split("v=")[-1]
    transcript = YouTubeTranscriptApi().fetch(video_id)
    text = " ".join(t.text for t in transcript)
    prompt = f"Summarize the following YouTube transcript:\n{text}"
    summary = get_summary(prompt)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)