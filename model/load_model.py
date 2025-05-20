import os
import gdown
import torch
from torchvision import transforms
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from PIL import Image, ImageDraw, ImageFont

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Download model if not present
MODEL_PATH = "Csm_Model.pth"
GDRIVE_FILE_ID = "1FrDwDnsD6UrDrD-0C8gygnO3Bk72Qyn0"
if not os.path.exists(MODEL_PATH):
    print("Model file not found. Downloading from Google Drive...")
    gdown.download(f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}", MODEL_PATH, quiet=False)

# Load the model
model = fasterrcnn_resnet50_fpn(pretrained=False, num_classes=10)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval().to(device)

CLASS_NAMES = [
    "Background", "Mask", "No helmet", "No mask", "No vest",
    "Person", "Cone", "Vest", "Machinery", "Vehicle"
]

transform = transforms.Compose([transforms.ToTensor()])

def detect_objects(image: Image.Image):
    img_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(img_tensor)[0]

    boxes = output["boxes"]
    labels = output["labels"]
    scores = output["scores"]

    draw = ImageDraw.Draw(image)
    detections = []

    for box, label, score in zip(boxes, labels, scores):
        if score > 0.5:
            box = box.cpu().numpy().astype(int)
            label_str = CLASS_NAMES[label]
            draw.rectangle(box.tolist(), outline="red", width=3)
            draw.text(
                (box[0], box[1] - 10), f"{label_str} ({score:.2f})", fill="red"
            )
            detections.append(label_str)

    return image, detections
