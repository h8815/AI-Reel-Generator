import os 
import time
import subprocess


def has_required_assets(folder: str) -> bool:
    base = f"user_uploads/{folder}"
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


def create_reel(folder, reel_name=None, transition="none", text_overlay="", aspect_ratio="9:16"):
    """
    Create a reel from the given folder with customization options
    """
    if reel_name is None:
        reel_name = folder
    
    output_path = f'static/reels/{reel_name}.mp4'
    
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
        text_clean = text_overlay.replace("'", "'\\''").replace(":", "\\:")
        text_filter = f"drawtext=text='{text_clean}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.5:boxborderw=10"
        vf_parts.append(text_filter)
    
    vf_string = ",".join(vf_parts)
    
    # Change to target directory
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
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            print(f"FFmpeg Error for {folder}:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            raise Exception(f"FFmpeg failed with return code {result.returncode}")
        
        print(f"Successfully created reel: {reel_name}")
        
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('static/reels', exist_ok=True)
    
    while True:
        print("Processing queue...")
        
        done_file = "done.txt"
        if not os.path.exists(done_file):
            with open(done_file, "w", encoding='utf-8') as f:
                pass
        
        with open(done_file, "r", encoding='utf-8') as f:
            done_folders = f.readlines()

        done_folders = [f.strip() for f in done_folders]
        
        if not os.path.exists("user_uploads"):
            os.makedirs("user_uploads", exist_ok=True)
            
        folders = os.listdir("user_uploads")
        
        for folder in folders:
            if folder not in done_folders:
                if has_required_assets(folder):
                    try:
                        # Read settings if available
                        settings_path = f"user_uploads/{folder}/settings.txt"
                        transition = "none"
                        text_overlay = ""
                        aspect_ratio = "9:16"
                        
                        if os.path.exists(settings_path):
                            with open(settings_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if '=' in line:
                                        key, value = line.strip().split('=', 1)
                                        if key == "transition":
                                            transition = value
                                        elif key == "text_overlay":
                                            text_overlay = value
                                        elif key == "aspect_ratio":
                                            aspect_ratio = value
                        
                        create_reel(folder, folder, transition, text_overlay, aspect_ratio)
                        with open(done_file, "a", encoding='utf-8') as f:
                            f.write(folder + "\n")
                    except Exception as e:
                        print(f"Error creating reel for {folder}: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"Skipping {folder} until audio.mp3 and input.txt with images are available")
        
        time.sleep(4)