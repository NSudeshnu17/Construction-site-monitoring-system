import torch
from torchvision import transforms
from torchvision.models.detection import fasterrcnn_resnet50_fpn
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
#device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model once globally
model = fasterrcnn_resnet50_fpn(pretrained=False, num_classes=10)  # your model config
model.load_state_dict(torch.load("Csm_Model.pth", map_location=device))
model.eval().to(device)

CLASS_NAMES = [
    "Background",
    "Mask",
    "No helmet",
    "No mask",
    "No vest",
    "Person",
    "Cone",
    "Vest",
    "Machinery",
    "Vehicle",
]

transform = transforms.Compose(
    [
        transforms.ToTensor(),
    ]
)


def detect_objects(image: Image.Image):
    img_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(img_tensor)[0]

    boxes = output["boxes"]
    labels = output["labels"]
    scores = output["scores"]

    draw = ImageDraw.Draw(image)
    detections = []

    # for box, label, score in zip(boxes, labels, scores):
    #     if score > 0.5:
    #         box = box.cpu().numpy().astype(int)
    #         label_str = CLASS_NAMES[label]
    #         draw.rectangle(box.tolist(), outline="red", width=3)
    #         draw.text(
    #             (box[0], box[1] - 10), f"{label_str} ({score:.2f})", fill="yellow"
    #         )
    #         detections.append(label_str)
    font = ImageFont.truetype("arial.ttf", size=15)  # Increase size here

    for box, label, score in zip(boxes, labels, scores):
        if score > 0.5:
            box = box.cpu().numpy().astype(int)
            label_str = CLASS_NAMES[label]
            draw.rectangle(box.tolist(), outline="red", width=3)
            draw.text(
                (box[0], box[1] - 25),
                f"{label_str} ({score:.2f})",
                fill="yellow",
                font=font,
            )
        detections.append(label_str)

    return image, detections
