from flask import Flask, request, render_template, send_from_directory
import os
import uuid
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
SEPARATED_FOLDER = 'separated'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SEPARATED_FOLDER, exist_ok=True)

# Allow downloading from separated folder
@app.route('/separated/<path:filename>')
def download_file(filename):
    return send_from_directory('separated', filename, as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = str(uuid.uuid4()) + ".mp3"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            subprocess.run(["demucs", "--two-stems=vocals", filepath], check=True)
        except subprocess.CalledProcessError:
            return "Error processing audio", 500

        songname = os.path.splitext(os.path.basename(filepath))[0]
        output_dir = os.path.join("separated", "htdemucs", songname)

        vocals_path = os.path.join(output_dir, "vocals.wav")
        instrumental_path = os.path.join(output_dir, "no_vocals.wav")

        return f"""
            <h2>Done!</h2>
            <a href="/{vocals_path}" target="_blank" download>Download Vocals</a><br>
            <a href="/{instrumental_path}" target="_blank" download>Download Instrumental</a>
        """
    return "No file uploaded", 400

if __name__ == '__main__':
    app.run(debug=True)
