from pathlib import Path
BASE = Path(__file__).resolve().parent
MODELS = BASE / "models"
DB_PATH = BASE / "database" / "rostos.db"
LANDMARKER = MODELS / "face_landmarker.task"
SFACE = MODELS / "face_recognition_sface_2021dec.onnx"
CAMERA_INDEX = 0
SAMPLES = 7
THRESHOLD = 0.45
CONSECUTIVE_FRAMES = 5
MIN_FACE = 100
