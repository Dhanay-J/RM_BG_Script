import sys, os, magic

if len(sys.argv) < 2:
    print("Usage : py main.py path/to/image ")
    print("Output : Will be in the same folder as input ")
    sys.exit(1)



def detect_file_type(file_path):
    """
    Detects the file type based on its content using python-magic.

    :param file_path: Path to the file
    :return: Detected file type
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception as e:
        return f"Error detecting file type: {e}"

if len(sys.argv) < 2:
    print("Usage : py main.py path/to/image ")
    print("Output : Will be in the same folder as input ")
    sys.exit(1)

input_image_path = sys.argv[1:][0]

# Check if the file exists
if not os.path.exists(input_image_path):
    print(f"File Not Found : {input_image_path}")
    sys.exit(1)

# Detect file type
file_type = detect_file_type(input_image_path)
if "image" in file_type:

    print(f"Removing BG from : {input_image_path}")

    from PIL import Image
    import matplotlib.pyplot as plt
    import torch
    from torchvision import transforms
    from transformers import AutoModelForImageSegmentation

    import warnings
    warnings.filterwarnings("ignore")
    

    model_name = 'briaai/RMBG-2.0'
    print(f"Loading model : {model_name}") 
    model = AutoModelForImageSegmentation.from_pretrained(model_name, trust_remote_code=True)
    torch.set_float32_matmul_precision(['high', 'highest'][0])
    model.to('cuda')
    model.eval()


    # Data settings
    print("Applying Transformations on Image")
    image_size = (1024, 1024)
    transform_image = transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])


    output_image_path = ''
    if input_image_path.endswith('.png'):
        output_image_path = input_image_path.replace('.png','_no_bg.png')
    elif input_image_path.endswith('.jpg'):
        output_image_path = input_image_path.replace('.jpg','_no_bg.png')
    elif input_image_path.endswith('.jpeg'):
        output_image_path = input_image_path.replace('.jpeg','_no_bg.png')

    image = Image.open(input_image_path)
    input_images = transform_image(image).unsqueeze(0).to('cuda')

    # Prediction
    with torch.no_grad():
        preds = model(input_images)[-1].sigmoid().cpu()
    pred = preds[0].squeeze()
    pred_pil = transforms.ToPILImage()(pred)
    mask = pred_pil.resize(image.size)
    image.putalpha(mask)


    image.save(output_image_path)
    print(f"Image saved as : {output_image_path}")

else:
    print(f"File Type Error : {input_image_path} if of Type {file_type}")
    sys.exit(1)

