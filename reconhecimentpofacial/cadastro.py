import cv2
import numpy as np
from camera import Camera, draw, quality, align
from banco import save_person
from config import SAMPLES

def feature(model, image):
    v=np.asarray(model.feature(image),dtype=np.float32).reshape(-1)
    n=np.linalg.norm(v)
    if not np.isfinite(v).all() or n<1e-8: raise ValueError("Embedding inválido")
    return v/n

def register(nome, model):
    samples=[]
    poses=["Olhe para frente","Vire um pouco à esquerda","Vire um pouco à direita",
           "Incline levemente a cabeça","Olhe para frente","Afaste-se um pouco","Aproxime-se um pouco"]
    cam=Camera()
    try:
        cam.open()
        while len(samples)<SAMPLES:
            frame,faces=cam.read()
            msg="Detectando rosto..."
            if len(faces)==1:
                ok,why=quality(frame,faces[0],len(faces))
                msg=why+" | ESPACO captura; ESC cancela" if ok else why
            elif len(faces)>1: msg="Mais de um rosto: apenas uma pessoa"
            draw(frame,faces)
            cv2.putText(frame,f"{poses[min(len(samples),len(poses)-1)]} | {len(samples)}/{SAMPLES}",(10,25),0,.55,(0,255,255),2)
            cv2.putText(frame,msg[:90],(10,55),0,.5,(0,255,255),1)
            cv2.imshow("Cadastro facial",frame); key=cv2.waitKey(1)&255
            if key==27: return False
            if key==32 and len(faces)==1 and quality(frame,faces[0],1)[0]:
                samples.append(feature(model,align(frame,faces[0])))
        save_person(nome,np.stack(samples)); print("Cadastro concluído; fotos não foram gravadas.")
        return True
    finally:
        cam.close(); cv2.destroyAllWindows()
