import cv2
from config import SFACE

def load_model():
    if not SFACE.exists(): raise FileNotFoundError(f"Falta modelo SFace: {SFACE}")
    model=cv2.FaceRecognizerSF.create(str(SFACE),"")
    if model is None: raise RuntimeError("OpenCV não carregou o SFace")
    return model

def menu():
    print("\n=== RECONHECIMENTO FACIAL ===\n1) Cadastrar pessoa\n2) Reconhecer rosto\n3) Listar cadastrados\n4) Excluir pessoa\n5) Sair")
    return input("Opção: ").strip()
