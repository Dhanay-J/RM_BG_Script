import os
import time
import io
import magic
import base64
import uuid
from flask import Flask, request, render_template, redirect, url_for
from PIL import Image
import torch
from torchvision import transforms
from transformers import AutoModelForImageSegmentation
import warnings
warnings.filterwarnings("ignore")

# Flask app
app = Flask(__name__)

# Directory to store uploaded and processed images
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4 MB limit

# PyTorch model (example setup)
model_name = 'briaai/RMBG-2.0'
print(f"Loading model : {model_name}") 
model = AutoModelForImageSegmentation.from_pretrained(model_name, trust_remote_code=True)
torch.set_float32_matmul_precision(['high', 'highest'][0])

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)

model.eval()

# Data settings
image_size = (1024, 1024)
transform_image = transforms.Compose([
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def detect_file_type(file_path):
    """Detect the file type based on its content using python-magic."""
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception as e:
        return f"Error detecting file type: {e}"

def process_image(input_image_path, output_image_path):
    """Process the input image and save the result."""
    image = Image.open(input_image_path).convert('RGB')
    input_images = transform_image(image).unsqueeze(0).to(device)

    # Prediction
    with torch.no_grad():
        preds = model(input_images)[-1].sigmoid().cpu()
    pred = preds[0].squeeze()
    pred_pil = transforms.ToPILImage()(pred)
    mask = pred_pil.resize(image.size)
    image.putalpha(mask)

    image.save(output_image_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No image file found", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # Generate a unique filename
        unique_id = str(uuid.uuid4())
        file_extension = file.filename.rsplit('.', 1)[-1].lower()
        unique_filename = f"{unique_id}.{file_extension}"
        input_image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(input_image_path)

        # Detect file type
        file_type = detect_file_type(input_image_path)
        if "image" not in file_type:
            os.remove(input_image_path)
            return "File is not an acceptable image file", 400

        # Process image
        output_file_name = f"processed_{unique_id}.png"
        output_image_path = os.path.join(app.config['PROCESSED_FOLDER'], output_file_name)
        process_image(input_image_path, output_image_path)

        # Schedule deletion of files after 5 minutes
        schedule_deletion(input_image_path)
        schedule_deletion(output_image_path)

        return redirect(url_for('download', filename=unique_filename))

@app.route('/download/<filename>')
def download(filename: str):
    unique_id = filename.rsplit('.', 1)[0]
    original_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    original_image = Image.open(original_image_path)
    img_width = original_image.width

    buffer = io.BytesIO()
    original_image.save(buffer, format=original_image.format)
    original_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    output_file_name = f"processed_{unique_id}.png"
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'], output_file_name)
    processed_image = Image.open(processed_image_path)
    buffer = io.BytesIO()
    processed_image.save(buffer, format="PNG")
    processed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    if not os.path.exists(original_image_path) or not os.path.exists(processed_image_path):
        return "File not found", 404

    return render_template('download.html', original_image=original_base64, processed_image=processed_base64, img_width=img_width)

def schedule_deletion(filepath):
    """Schedule the deletion of files after a specified time."""
    def delete_file():
        time.sleep(300)  # In seconds
        if os.path.exists(filepath):
            os.remove(filepath)

    import threading
    threading.Thread(target=delete_file).start()

if __name__ == '__main__':
    app.run()

# Use a production WSGI server for deployment