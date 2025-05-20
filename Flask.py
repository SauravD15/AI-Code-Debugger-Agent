from flask import Flask, render_template, request
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image

# Initialize Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "api key")
genai.configure(api_key=GEMINI_API_KEY)

# Analyze the code using Gemini
def analyze_code(code_snippet):
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt_comments = f"You are an AI assistant that explains code and rewrite it with very simple comments for all lines (keep comments on same line as code and add _______ between code and comments), using everyday language so that even a beginner can understand. And humanize it. Also make a block diagram of the code (don't bold, italicize or underline anything).\n\n{code_snippet}"
    response_comments = model.generate_content(prompt_comments)

    prompt_debug = f"Analyze the following code for errors and suggest possible fixes in very simple steps and what it's used for (don't bold, italicize or underline anything).\n\n{code_snippet}"
    response_debug = model.generate_content(prompt_debug)

    return response_comments.text, response_debug.text

# Route
@app.route("/", methods=["GET", "POST"])
def index():
    comments, debugging_suggestions, code_snippet = "", "", ""

    if request.method == "POST":
        file = request.files.get("file")
        code_snippet = request.form.get("code", "")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            # Extract code based on file type
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                img = Image.open(filepath)
                code_snippet = pytesseract.image_to_string(img)
            else:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    code_snippet = f.read()

        if code_snippet.strip():
            comments, debugging_suggestions = analyze_code(code_snippet)

    return render_template("index.html", comments=comments, debugging_suggestions=debugging_suggestions, code=code_snippet)

if __name__ == "__main__":
    app.run(debug=True)
