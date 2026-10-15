import cv2
import numpy as np
from camera import Camera, draw, align
from banco import embeddings
from config import THRESHOLD, CONSECUTIVE_FRAMES
from math_utils import cosine


def identify(v, people):
    best_name=None; best=-1.0
    for p in people:
        s=cosine(v,p["embedding"])
        if s>best: best_name,best=p["nome"],s
    return (best_name if best>=THRESHOLD else None),best

def recognize(model):
    people=embeddings()
    if not people: print("Banco vazio; cadastre alguém primeiro."); return
    cam=Camera(); last=None; count=0; decision=None
    try:
        cam.open()
        while True:
            frame,faces=cam.read(); text="Detectando rosto..."; color=(0,220,255)
            if len(faces)>1:
                text="ACESSO NEGADO: mais de um rosto"; color=(0,0,255); last=None; count=0; decision=None
            elif len(faces)==1:
                x,y,w,h=faces[0]["bbox"]
                try:
                    v=np.asarray(model.feature(align(frame,faces[0])),dtype=np.float32).reshape(-1)
                    v/=max(float(np.linalg.norm(v)),1e-8)
                    name,score=identify(v,people); candidate=name or "__desconhecido__"
                    count=count+1 if candidate==last else 1
                    last=candidate
                    if count>=CONSECUTIVE_FRAMES: decision=name if name else False
                    if decision is not None and decision is not False: text=f"ACESSO LIBERADO: {decision}"; color=(0,180,0)
                    elif decision is False: text="ACESSO NEGADO: Pessoa não cadastrada"; color=(0,0,255)
                    else: text=f"Verificando {count}/{CONSECUTIVE_FRAMES}"
                    cv2.putText(frame,f"Similaridade: {score:.3f}",(10,60),0,.65,color,2)
                except (ValueError,cv2.error) as e: text=f"Erro de reconhecimento: {e}"
                cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
            else: last=None; count=0; decision=None
            draw(frame,faces); cv2.putText(frame,text[:100],(10,30),0,.55,color,2)
            cv2.putText(frame,"ESC: sair",(10,frame.shape[0]-10),0,.5,(255,255,255),1)
            cv2.imshow("Reconhecimento facial",frame)
            if cv2.waitKey(1)&255==27: break
    finally: cam.close(); cv2.destroyAllWindows()
