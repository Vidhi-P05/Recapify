from flask import Flask, render_template, request, redirect, url_for, flash
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-for-recapify')

# Configure Gemini API
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))


def get_video_id(url):
    """Extract the video ID from the YouTube URL."""
    if "?v=" in url:
        return url.split("?v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "/embed/" in url:
        return url.split("/embed/")[1].split("?")[0]
    elif "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")


def get_video_details(video_id):
    """Get video title and thumbnail using iframe embed approach."""
    # Since we'll be embedding the video, we don't need to fetch metadata separately
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    return {
        "thumbnail": thumbnail_url,
        "embed_url": f"https://www.youtube.com/embed/{video_id}"
    }


def fetch_transcript(video_id):
    """Fetch the transcript of a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None


def summarize_text_with_prompt(text, prompt):
    """Summarize the text using the Google Gemini API with a custom prompt."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"{prompt}: {text}")
        return response.text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    youtube_url = request.form.get('youtube_url')
    prompt = request.form.get('prompt', 'Summarize the main points of this video')

    try:
        # Extract the video ID
        video_id = get_video_id(youtube_url)

        # Get video details
        video_details = get_video_details(video_id)

        # Fetch the transcript
        transcript = fetch_transcript(video_id)
        if not transcript:
            flash("Couldn't retrieve transcript for this video. It may not have captions available.")
            return redirect(url_for('index'))

        # Summarize the transcript
        summary = summarize_text_with_prompt(transcript, prompt)
        if not summary:
            flash("Couldn't generate a summary. Please try again.")
            return redirect(url_for('index'))

        return render_template('result.html',
                               summary=summary,
                               video_id=video_id,
                               video_details=video_details,
                               prompt=prompt)

    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)