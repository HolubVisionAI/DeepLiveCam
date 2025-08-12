from fastapi import FastAPI, WebSocket, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # added import
import uvicorn
import cv2
import base64
import asyncio
import numpy as np
from modules.processors.frame.face_swapper import process_frame

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve client pages
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Global to hold the uploaded source face
uploaded_source_face = None


@app.post("/upload-face")
async def upload_face(file: UploadFile = File(...)):
    content = await file.read()
    np_arr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    from modules.face_analyser import get_one_face  # imported locally

    face = get_one_face(img)
    global uploaded_source_face
    if face is None:
        return {"error": "No face detected in uploaded image"}
    uploaded_source_face = face
    return {"status": "Face uploaded and processed"}


@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)  # Default webcam; adjust index if needed
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Use process_frame with the uploaded source face if available
            if uploaded_source_face is not None:
                processed_frame = process_frame(uploaded_source_face, frame)
            else:
                processed_frame = frame  # fall back to raw frame if no face uploaded
            _, buffer = cv2.imencode('.jpg', processed_frame)
            jpg_as_text = base64.b64encode(buffer).decode()
            await websocket.send_text(jpg_as_text)
            await asyncio.sleep(0.033)  # ~30 FPS
    except Exception as e:
        print("WS error:", e)
    finally:
        cap.release()
        await websocket.close()


# New endpoint to process frames received from client webcam stream
@app.websocket("/ws/client-stream")
async def client_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive a base64-encoded frame from client
            data = await websocket.receive_text()
            img_bytes = base64.b64decode(data)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            # Process the frame if a face was uploaded, else use raw frame
            if uploaded_source_face is not None:
                processed_frame = process_frame(uploaded_source_face, frame)
            else:
                processed_frame = frame
            _, buffer = cv2.imencode('.jpg', processed_frame)
            processed_base64 = base64.b64encode(buffer).decode()
            await websocket.send_text(processed_base64)
    except Exception as e:
        print("Client stream error:", e)
    finally:
        await websocket.close()


@app.get("/")
def read_root():
    # ...existing code for health check...
    return {"status": "Server is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
