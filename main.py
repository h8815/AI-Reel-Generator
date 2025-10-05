from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import uuid
from werkzeug.utils import secure_filename
import os
import subprocess
import shutil
import json
from datetime import datetime

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB for images
MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB for audio

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB total


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        print("=== Starting Reel Creation ===")
        print("Form data:", request.form)
        print("Files:", list(request.files.keys()))
        
        rec_id = request.form.get("uuid")
        reel_name = request.form.get("reel_name", "").strip()
        
        # Get customization options
        image_duration = request.form.get("image_duration", "1")
        transition = request.form.get("transition", "none")
        text_overlay = request.form.get("text_overlay", "").strip()
        aspect_ratio = request.form.get("aspect_ratio", "9:16")
        
        input_files = []

        # Validate reel name
        if not reel_name:
            return render_template("create.html", myid=myid, 
                                 error="Please provide a name for your reel.")
        
        # Sanitize reel name
        reel_name = secure_filename(reel_name)
        if not reel_name:
            return render_template("create.html", myid=myid, 
                                 error="Invalid reel name. Please use only letters, numbers, and underscores.")

        # Validate image duration
        try:
            duration = float(image_duration)
            if duration < 0.5 or duration > 10:
                return render_template("create.html", myid=myid, 
                                     error="Image duration must be between 0.5 and 10 seconds.")
        except ValueError:
            return render_template("create.html", myid=myid, 
                                 error="Invalid image duration value.")

        # Check if FFmpeg is installed
        if not check_ffmpeg():
            return render_template("create.html", myid=myid, 
                                 error="FFmpeg is not installed. Please install FFmpeg to create reels.")

        target_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(rec_id))
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)

        # Process audio file
        audio_file = request.files.get('audio')
        has_audio = False
        if audio_file and audio_file.filename:
            audio_file.seek(0, os.SEEK_END)
            audio_size = audio_file.tell()
            audio_file.seek(0)
            
            if audio_size > MAX_AUDIO_SIZE:
                return render_template("create.html", myid=myid, 
                                     error=f"Audio file is too large. Maximum size is {MAX_AUDIO_SIZE // (1024*1024)}MB.")
            
            audio_filename = secure_filename(audio_file.filename)
            audio_ext = os.path.splitext(audio_filename)[1].lower()
            if audio_ext == '.mp3':
                audio_path = os.path.join(target_folder, 'audio.mp3')
                audio_file.save(audio_path)
                has_audio = True
                print(f'Saved audio.mp3 at {audio_path}')
            else:
                return render_template("create.html", myid=myid, 
                                     error="Invalid audio format. Only MP3 files are allowed.")
        else:
            return render_template("create.html", myid=myid, 
                                 error="Please upload an audio file.")
        
        # Process image files - collect them in order
        file_keys = sorted([key for key in request.files.keys() if key.startswith('file')])
        print(f"Processing {len(file_keys)} image files")
        
        for key in file_keys:
            file = request.files[key]
            if file and file.filename:
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    return render_template("create.html", myid=myid, 
                                         error=f"One or more images are too large. Maximum size per image is {MAX_FILE_SIZE // (1024*1024)}MB.")
                
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1].lower().lstrip('.')
                if ext in ALLOWED_EXTENSIONS:
                    # Save with index to maintain order
                    new_filename = f"img_{len(input_files):03d}{os.path.splitext(filename)[1]}"
                    file_path = os.path.join(target_folder, new_filename)
                    file.save(file_path)
                    input_files.append(new_filename)
                    print(f"Saved image: {new_filename}")

        if not input_files:
            return render_template("create.html", myid=myid, 
                                 error="Please upload at least one image (JPG, JPEG, or PNG).")

        print(f"Total images saved: {len(input_files)}")

        if has_audio and input_files:
            # Create input.txt for FFmpeg concat
            input_txt_path = os.path.join(target_folder, "input.txt")
            with open(input_txt_path, "w", encoding='utf-8') as f:
                for fl in input_files:
                    f.write(f"file '{fl}'\n")
                    f.write(f"duration {duration}\n")
                # Add the last file again without duration
                f.write(f"file '{input_files[-1]}'\n")
            
            print(f"Created input.txt with {len(input_files)} images")
            
            # Save customization settings
            settings_path = os.path.join(target_folder, "settings.txt")
            with open(settings_path, "w", encoding='utf-8') as f:
                f.write(f"transition={transition}\n")
                f.write(f"text_overlay={text_overlay}\n")
                f.write(f"aspect_ratio={aspect_ratio}\n")
            
            # Ensure reels directory exists
            reels_dir = os.path.join("static", "reels")
            if not os.path.exists(reels_dir):
                os.makedirs(reels_dir, exist_ok=True)
            
            # Create metadata file for gallery
            metadata_dir = os.path.join("static", "metadata")
            if not os.path.exists(metadata_dir):
                os.makedirs(metadata_dir, exist_ok=True)
            
            # Create reel
            if has_required_assets(str(rec_id)):
                try:
                    create_reel(str(rec_id), reel_name, transition, text_overlay, aspect_ratio)
                    
                    # Save metadata
                    metadata = {
                        "name": reel_name,
                        "created_at": datetime.now().isoformat(),
                        "image_count": len(input_files),
                        "duration": duration,
                        "transition": transition,
                        "text_overlay": text_overlay,
                        "aspect_ratio": aspect_ratio
                    }
                    metadata_path = os.path.join(metadata_dir, f"{reel_name}.json")
                    with open(metadata_path, "w", encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2)
                    
                    return render_template("create.html", myid=myid, 
                                         success=f"Reel '{reel_name}' created successfully with {len(input_files)} images! Go and watch it in the gallery section.",
                                         show_gallery_link=True)
                except Exception as e:
                    print(f"Error creating reel: {e}")
                    import traceback
                    traceback.print_exc()
                    return render_template("create.html", myid=myid, 
                                         error=f"Error creating reel: {str(e)}. Please check the console for details.")
            else:
                return render_template("create.html", myid=myid, 
                                     error="Missing required assets for reel creation.")
        else:
            return render_template("create.html", myid=myid, 
                                 error="Please provide both audio and images.")

    return render_template("create.html", myid=myid)


@app.route("/gallery")
def gallery():
    reels_dir = os.path.join("static", "reels")
    metadata_dir = os.path.join("static", "metadata")
    
    if not os.path.exists(reels_dir):
        os.makedirs(reels_dir, exist_ok=True)
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir, exist_ok=True)
    
    reels = []
    for filename in os.listdir(reels_dir):
        if filename.endswith(".mp4"):
            reel_info = {
                "filename": filename,
                "name": os.path.splitext(filename)[0],
                "size": os.path.getsize(os.path.join(reels_dir, filename)),
                "created_at": datetime.fromtimestamp(os.path.getctime(os.path.join(reels_dir, filename))).strftime("%Y-%m-%d %H:%M")
            }
            
            # Load metadata if exists
            metadata_path = os.path.join(metadata_dir, f"{os.path.splitext(filename)[0]}.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        reel_info.update(metadata)
                except:
                    pass
            
            reels.append(reel_info)
    
    # Sort by creation date (newest first)
    reels.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    print("Gallery reels:", [r['filename'] for r in reels])
    return render_template("gallery.html", reels=reels)


@app.route("/delete/<reel_name>", methods=["POST"])
def delete_reel(reel_name):
    try:
        reel_path = os.path.join("static", "reels", secure_filename(reel_name))
        metadata_path = os.path.join("static", "metadata", f"{os.path.splitext(secure_filename(reel_name))[0]}.json")
        
        if os.path.exists(reel_path):
            os.remove(reel_path)
        
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            
        return jsonify({"success": True, "message": "Reel deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/help")
def help():
    return render_template("help.html")


def has_required_assets(folder: str) -> bool:
    base = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    audio_path = os.path.join(base, 'audio.mp3')
    input_path = os.path.join(base, 'input.txt')

    if not os.path.exists(audio_path):
        print(f"Missing audio.mp3 for {folder}")
        return False
    if not os.path.exists(input_path):
        print(f"Missing input.txt for {folder}")
        return False

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if "file '" not in content:
            print(f"input.txt has no image entries for {folder}")
            return False
    except Exception as e:
        print(f"Error reading input.txt for {folder}: {e}")
        return False

    return True


def create_reel(folder, reel_name, transition="none", text_overlay="", aspect_ratio="9:16"):
    output_path = os.path.join('static', 'reels', f'{reel_name}.mp4')
    input_txt = os.path.join('user_uploads', folder, 'input.txt')
    audio_path = os.path.join('user_uploads', folder, 'audio.mp3')
    
    # Set dimensions based on aspect ratio
    if aspect_ratio == "9:16":
        width, height = 1080, 1920
    elif aspect_ratio == "16:9":
        width, height = 1920, 1080
    elif aspect_ratio == "1:1":
        width, height = 1080, 1080
    else:
        width, height = 1080, 1920
    
    # Build video filter
    vf_parts = [
        f"scale={width}:{height}:force_original_aspect_ratio=decrease",
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"
    ]
    
    # Add transition effect
    if transition == "fade":
        vf_parts.append("fade=t=in:st=0:d=0.5")
    
    # Add text overlay if provided
    if text_overlay:
        # Escape special characters for FFmpeg
        text_clean = text_overlay.replace("'", "'\\''").replace(":", "\\:")
        # Use Arial or default font
        text_filter = f"drawtext=text='{text_clean}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.5:boxborderw=10"
        vf_parts.append(text_filter)
    
    vf_string = ",".join(vf_parts)
    
    # Change working directory to process files correctly
    original_dir = os.getcwd()
    target_dir = os.path.join(original_dir, 'user_uploads', folder)
    
    try:
        os.chdir(target_dir)
        
        command = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', 'input.txt',
            '-i', 'audio.mp3',
            '-vf', vf_string,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-r', '30',
            '-pix_fmt', 'yuv420p',
            os.path.join(original_dir, output_path)
        ]
        
        print(f"Running FFmpeg command: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print("FFmpeg STDOUT:", result.stdout)
            print("FFmpeg STDERR:", result.stderr)
            raise Exception(f"FFmpeg failed with return code {result.returncode}")
        
        print(f"Successfully created reel: {reel_name}")
        
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('user_uploads', exist_ok=True)
    os.makedirs('static/reels', exist_ok=True)
    os.makedirs('static/metadata', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)