# reconhecimentpofacial

Protótipo educacional de controle de acesso por reconhecimento facial. Não é um sistema de segurança certificado e não deve comandar uma fechadura real sem validação profissional.

## Tecnologias e modelo
Python 3.10/3.11, OpenCV contrib, MediaPipe Tasks FaceLandmarker, NumPy e SQLite. O MediaPipe fornece landmarks, não identidade. O embedding usa **SFace ONNX** integrado em `cv2.FaceRecognizerSF`, evitando dependência extra de runtime ONNX. O recorte é alinhado pela linha dos olhos e redimensionado para 112×112; `feature()` do wrapper OpenCV executa o pré-processamento previsto para SFace.

## Instalação no Windows
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Linux/macOS: crie/ative o venv com `python3.11 -m venv .venv` e `source .venv/bin/activate`; instale `requirements.txt`.

## Modelos
Crie `models/` e baixe:
- MediaPipe: salve como `models/face_landmarker.task`: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
- SFace: no OpenCV Zoo, pasta `models/face_recognition_sface`, baixe `face_recognition_sface_2021dec.onnx`: https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface

Os modelos não são incluídos no repositório por serem arquivos binários grandes. Confira os nomes exatamente.

## Executar e usar
```powershell
python main.py
```
1 cadastra (ajuste a pose e pressione ESPAÇO para cada amostra; ESC cancela), 2 reconhece, 3 lista, 4 exclui por ID, 5 sai. São usadas 7 amostras válidas e apenas embeddings são guardados. O banco é criado automaticamente em `database/rostos.db`.

## Similaridade e calibração
Embedding é um vetor numérico de características aprendidas. Similaridade de cosseno é `dot(a,b)/(norm(a)*norm(b))`; perto de 1 indica vetores mais próximos. `THRESHOLD=0.45` é somente um valor inicial, não universal. Colete scores de pessoas cadastradas e não cadastradas em condições reais e ajuste o limite: aumentar o limite geralmente reduz falsos aceites e aumenta falsas rejeições. Valide em amostras separadas. A confirmação em 5 frames reduz oscilações, mas não prova identidade.

## Testes
```powershell
python -m unittest discover -s tests -v
python -m compileall .
```
Os testes unitários cobrem banco e similaridade sem webcam/modelos. Não pude testar fisicamente sua câmera neste ambiente.

## Problemas
- Webcam não abre: feche apps que usam câmera, confira permissões e altere `CAMERA_INDEX` em `config.py`.
- Rosto não detectado: melhore iluminação, aproxime-se e confira `face_landmarker.task`.
- SFace não carrega: confira ONNX, use `opencv-contrib-python` (não instale `opencv-python` junto).
- Erro de dependências: Python 3.10/3.11 64-bit e ambiente virtual limpo.
- Múltiplos rostos: o cadastro só aceita um; no reconhecimento o sistema nega se houver mais de um.

## Segurança, LGPD e hardware
Fotos ou vídeos em celular podem enganar o sistema. Liveness por piscada pode ser adicionado com landmarks dos olhos, mas não é defesa robusta; vídeos também piscam. Produção exige PAD validado, limitação de tentativas, logs protegidos, criptografia e segundo fator. Biometria é dado pessoal sensível na LGPD (Lei 13.709/2018): determine base legal/finalidade, informe titulares, obtenha consentimento quando aplicável, limite retenção e acesso e implemente exclusão.

Exemplos ilustrativos para integração futura (não conectados ao fluxo):
```python
def liberar_acesso_gpio(pino, duracao=3):
    from gpiozero import OutputDevice
    import time
    rele = OutputDevice(pino, active_high=True, initial_value=False)
    try:
        rele.on(); time.sleep(duracao); rele.off()
    finally: rele.close()

def liberar_acesso_serial(porta="COM3", baudrate=9600):
    import serial
    with serial.Serial(porta, baudrate, timeout=2) as s:
        s.write(b"UNLOCK\\n")
        if s.readline().decode("ascii", errors="replace").strip() != "OK":
            raise RuntimeError("Controlador não confirmou.")
```
Instale dependências opcionais com `pip install gpiozero` (Raspberry Pi) ou `pip install pyserial`. Nunca conecte uma fechadura diretamente ao PC/GPIO: use interface/relé isolado, fonte adequada e técnico qualificado. Fail-secure tende a permanecer trancada sem energia; fail-safe destranca sem energia e pode ser exigida em rotas de fuga. Decida conforme normas locais, análise de risco e profissional habilitado.

## GitHub
Crie um repositório vazio chamado `reconhecimentpofacial`, depois execute na pasta do projeto:
```powershell
git init
git add .
git commit -m "Projeto inicial de reconhecimento facial"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/reconhecimentpofacial.git
git push -u origin main
```
Não envie banco de dados real nem modelos biométricos ou imagens ao Git.
