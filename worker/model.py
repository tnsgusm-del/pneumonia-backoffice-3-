import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image

# ── 디바이스 설정 ─────────────────────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── SimpleCNN 모델 정의 ───────────────────────────────────
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 32 * 32, 2),
        )

    def forward(self, x):
        return self.fc(self.conv(x))

# ── 모델 로드 (서버 시작 시 1회만 실행) ──────────────────────
MODEL_PATH = "worker/models/model_state_dict.pth"

def load_model():
    model = SimpleCNN()
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device, weights_only=True))
    model = model.to(device)
    model.eval()
    return model

model = load_model()

# ── 이미지 전처리 ─────────────────────────────────────────
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5]),
])

# ── 예측 함수 ─────────────────────────────────────────────
def predict(image_path: str) -> dict:
    image = Image.open(image_path).convert("L")
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1)
        confidence = probabilities[0][1].item()
        is_pneumonia = confidence >= 0.5

    return {
        "is_pneumonia": bool(is_pneumonia),
        "confidence": round(confidence, 4),
    }
