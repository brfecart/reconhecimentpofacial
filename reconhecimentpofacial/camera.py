import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from config import LANDMARKER, CAMERA_INDEX, MIN_FACE

class Camera:
    def __init__(self):
        if not LANDMARKER.exists():
            raise FileNotFoundError(f"Falta o modelo MediaPipe: {LANDMARKER}")
        opts = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(LANDMARKER)),
            running_mode=vision.RunningMode.VIDEO, num_faces=2)
        self.detector = vision.FaceLandmarker.create_from_options(opts)
        self.cap = None
        self.ts = 0

    def open(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            self.close()
            raise RuntimeError("Webcam não abriu. Verifique permissões ou CAMERA_INDEX.")
        return self

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Falha ao ler a webcam.")
        frame = cv2.flip(frame, 1)
        self.ts += 33
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.detector.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), self.ts)
        h, w = frame.shape[:2]
        faces = []
        for lm in result.face_landmarks:
            xs, ys = [p.x*w for p in lm], [p.y*h for p in lm]
            x1, y1, x2, y2 = max(0,int(min(xs))), max(0,int(min(ys))), min(w,int(max(xs))), min(h,int(max(ys)))
            faces.append({"landmarks": lm, "bbox": (x1,y1,x2-x1,y2-y1)})
        return frame, faces

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if getattr(self, "detector", None):
            self.detector.close()
            self.detector = None

    def __enter__(self):
        return self.open()

    def __exit__(self, *_):
        self.close()

def draw(frame, faces):
    h,w = frame.shape[:2]
    for face in faces:
        for p in face["landmarks"]:
            cv2.circle(frame, (int(p.x*w), int(p.y*h)), 1, (0,220,100), -1)
        x,y,bw,bh = face["bbox"]
        cv2.rectangle(frame,(x,y),(x+bw,y+bh),(0,220,100),2)
    return frame

def quality(frame, face, count):
    import numpy as np
    if count != 1: return False, "Mantenha apenas um rosto"
    x,y,w,h = face["bbox"]
    if min(w,h) < MIN_FACE: return False, "Aproxime o rosto"
    crop = frame[y:y+h,x:x+w]
    gray = cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
    if cv2.Laplacian(gray,cv2.CV_64F).var() < 35: return False, "Imagem borrada"
    if not 35 < float(np.mean(gray)) < 225: return False, "Ajuste a iluminação"
    return True, "Amostra válida"

def align(frame, face):
    import numpy as np
    lm=face["landmarks"]; h,w=frame.shape[:2]
    a=np.array([lm[33].x*w,lm[33].y*h],np.float32)
    b=np.array([lm[263].x*w,lm[263].y*h],np.float32)
    center=tuple((a+b)/2)
    angle=float(np.degrees(np.arctan2(b[1]-a[1],b[0]-a[0])))
    mat=cv2.getRotationMatrix2D(center,angle,1.0)
    rotated=cv2.warpAffine(frame,mat,(w,h),borderMode=cv2.BORDER_REPLICATE)
    x,y,bw,bh=face["bbox"]; cx=x+bw/2; cy=y+bh/2
    x1=max(0,int(cx-bw*.625)); x2=min(w,int(cx+bw*.625))
    y1=max(0,int(cy-bh*.625)); y2=min(h,int(cy+bh*.625))
    crop=rotated[y1:y2,x1:x2]
    if crop.size == 0: raise ValueError("Recorte facial vazio")
    return cv2.resize(crop,(112,112))
