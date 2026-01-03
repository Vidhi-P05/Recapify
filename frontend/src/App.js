import React, { useState } from "react";  // React and state management
import axios from "axios";                // To make API calls
import ReactMarkdown from "react-markdown"; // For rendering markdown
import "./App.css";                       // Styling

function App() {
  const [text, setText] = useState("");           // Store text input
  const [summary, setSummary] = useState("");     // Store summary output
  const [file, setFile] = useState(null);         // Store uploaded PDF file
  const [youtubeURL, setYoutubeURL] = useState(""); // Store YouTube URL
  const [mode, setMode] = useState("text");       // Store selected input mode
  const [loading, setLoading] = useState(false);  // Show loading

  // Function runs when user clicks summarize
  const handleSummarize = async () => {
    setLoading(true);      // Start loading
    setSummary("");        // Clear summary

    try {
      let res;

      // If text is selected
      if (mode === "text") {
        if (!text.trim()) return alert("Please enter some text.");
        res = await axios.post("http://localhost:5000/summarize/text", { text });
      }

      // If PDF is selected
      else if (mode === "pdf") {
        if (!file) return alert("Please upload a PDF file.");
        const formData = new FormData();
        formData.append("file", file);
        res = await axios.post("http://localhost:5000/summarize/pdf", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      // If YouTube is selected
      else if (mode === "youtube") {
        if (!youtubeURL.trim()) return alert("Please enter a YouTube URL.");
        res = await axios.post("http://localhost:5000/summarize/youtube", { url: youtubeURL });
      }

      setSummary(res.data.summary);  // Show result

    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
    }

    setLoading(false);  // Stop loading
  };

  return (
    <div className="app">
      <h1>Recapify: AI Summarizer</h1>

      
<div className="mode-buttons">
  <button
    className={mode === "text" ? "active" : ""}
    onClick={() => setMode("text")}
  >
    Text
  </button>
  <button
    className={mode === "pdf" ? "active" : ""}
    onClick={() => setMode("pdf")}
  >
    PDF
  </button>
  <button
    className={mode === "youtube" ? "active" : ""}
    onClick={() => setMode("youtube")}
  >
    YouTube
  </button>
</div>

      {/* Text input */}
      {mode === "text" && (
        <textarea
          placeholder="Paste your text here..."
          rows="10"
          value={text}
          onChange={(e) => setText(e.target.value)}
        ></textarea>
      )}

      {/* PDF file input */}
      {mode === "pdf" && (
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
      )}

      {/* YouTube input */}
      {mode === "youtube" && (
        <input
          type="text"
          placeholder="Enter YouTube video URL..."
          value={youtubeURL}
          onChange={(e) => setYoutubeURL(e.target.value)}
        />
      )}

      {/* Summarize button */}
      <button className='smz-button' onClick={handleSummarize} disabled={loading}>
        {loading ? "Summarizing..." : "Summarize"}
      </button>

      {/* Display Summary */}
      {summary && (
        <div className="summary">
          <h2>Summary</h2>
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export default App;