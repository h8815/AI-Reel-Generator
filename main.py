from flask import Flask, render_template, request
import uuid
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        print(request.files.keys())
        rec_id = request.form.get("uuid")
        input_files = []

        target_folder = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)

        audio_file = request.files.get('audio')
        has_audio = False
        if audio_file and audio_file.filename:
            audio_filename = secure_filename(audio_file.filename)
            audio_ext = os.path.splitext(audio_filename)[1].lower()
            if audio_ext == '.mp3':
                audio_file.save(os.path.join(target_folder, 'audio.mp3'))
                has_audio = True
                print('Saved audio.mp3')
            else:
                print('Invalid audio format, only .mp3 allowed')
        else:
            print('No audio file provided')
        for key, value in request.files.items():
            if key == 'audio':
                continue
            file = request.files[key]
            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1].lower().lstrip('.')
                if ext in ALLOWED_EXTENSIONS:
                    file.save(os.path.join(target_folder, filename))
                    input_files.append(filename)
                    print(filename)
                else:
                    print(f"Skipped non-image file: {filename}")

        if has_audio and input_files:
            for fl in input_files:
                with open(os.path.join(target_folder,  "input.txt"), "a") as f:
                    f.write(f"file '{fl}'\n")
                    f.write("duration 1\n")
        else:
            print("Missing audio or images; not writing input.txt")

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels = os.listdir("static/reels")
    print(reels)
    return render_template("gallery.html", reels=reels)

app.run(debug=True)