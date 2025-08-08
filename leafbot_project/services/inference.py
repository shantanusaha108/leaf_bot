import torch
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import os
from logger import log_error

class PlantDiseaseClassifier(torch.nn.Module):
    def __init__(self, num_classes, dropout_rate=0.3):
        super().__init__()
        self.backbone = models.efficientnet_b2(pretrained=False)
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = torch.nn.Identity()
        self.attention = torch.nn.Sequential(
            torch.nn.AdaptiveAvgPool2d(1),
            torch.nn.Flatten(),
            torch.nn.Linear(num_features, num_features // 4),
            torch.nn.ReLU(),
            torch.nn.Linear(num_features // 4, num_features),
            torch.nn.Sigmoid()
        )
        self.classifier = torch.nn.Sequential(
            torch.nn.Dropout(dropout_rate),
            torch.nn.Linear(num_features, 512),
            torch.nn.BatchNorm1d(512),
            torch.nn.ReLU(),
            torch.nn.Dropout(dropout_rate * 0.5),
            torch.nn.Linear(512, 256),
            torch.nn.BatchNorm1d(256),
            torch.nn.ReLU(),
            torch.nn.Dropout(dropout_rate * 0.3),
            torch.nn.Linear(256, num_classes)
        )

    def forward(self, x):
        features = self.backbone.features(x)
        pooled = torch.nn.functional.adaptive_avg_pool2d(features, 1)
        pooled = torch.flatten(pooled, 1)
        attention_weights = self.attention(features)
        attended_features = pooled * attention_weights
        return self.classifier(attended_features)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'plant_disease_model.pth')

_model = None
_class_names = None

def load_model():
    global _model, _class_names
    if _model is None:
        try:
            checkpoint = torch.load(MODEL_PATH, map_location='cpu')
            _class_names = checkpoint['class_names']
            num_classes = len(_class_names)
            _model = PlantDiseaseClassifier(num_classes)
            _model.load_state_dict(checkpoint['model_state_dict'])
            _model.eval()
        except Exception as e:
            log_error("ModelLoadError", f"Failed to load model: {e}")
            raise
    return _model, _class_names

def predict_image(uploaded_file):
    try:
        model, class_names = load_model()
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        image = Image.open(uploaded_file).convert('RGB')
        image_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)[0]

        top_probs, top_indices = torch.topk(probabilities, 3)
        return [
            {"label": class_names[top_indices[i].item()],
             "score": round(top_probs[i].item(), 4)}
            for i in range(len(top_indices))
        ]
    except Exception as e:
        log_error("PredictionError", f"Image prediction failed: {e}")
        raise
