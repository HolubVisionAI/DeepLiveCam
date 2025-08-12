import asyncio
import websockets  # pip install websockets
import base64
import cv2
import numpy as np
import requests
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import io

# Global flag and queue for UI updates
streaming_flag = False
frame_queue = queue.Queue()


async def stream_webcam():
    uri = "ws://192.168.1.14:8000/ws/client-stream"  # update server IP if needed
    cap = cv2.VideoCapture(0)
    try:
        async with websockets.connect(uri) as websocket:
            while streaming_flag:
                ret, frame = cap.read()
                if not ret:
                    continue
                # Encode frame as JPEG and send
                _, buffer = cv2.imencode('.jpg', frame)
                base64_frame = base64.b64encode(buffer).decode()
                await websocket.send(base64_frame)
                response = await websocket.recv()
                processed_bytes = base64.b64decode(response)
                np_arr = np.frombuffer(processed_bytes, np.uint8)
                processed_frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                # Convert frame to PNG bytes for Tkinter display
                _, png_buffer = cv2.imencode('.png', processed_frame)
                frame_queue.put(png_buffer.tobytes())
                await asyncio.sleep(0)  # yield control
    finally:
        cap.release()


def start_stream():
    global streaming_flag
    streaming_flag = True
    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: loop.run_until_complete(stream_webcam()), daemon=True).start()


def stop_stream():
    global streaming_flag
    streaming_flag = False


def upload_face_image():
    face_image_path = filedialog.askopenfilename(
        title="Select Face Image",
        filetypes=[
            ("Image Files", ("*.png", "*.jpg", "*.jpeg")),  # updated filetypes tuple
            ("All Files", "*.*")
        ]
    )
    if face_image_path:
        url = "http://192.168.1.14:8000/upload-face"  # update if needed
        with open(face_image_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files)
            result = response.json()
            messagebox.showinfo("Upload Response", result.get("status") or result.get("error"))


# Build a simple UI with Tkinter
root = tk.Tk()
root.title("Deep Live Cam Client")
root.geometry("800x600")  # Set default window size

# Create a frame for buttons and pack them in one line
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

btn_upload = tk.Button(button_frame, text="Upload Face", command=upload_face_image)
btn_start = tk.Button(button_frame, text="Start Stream", command=start_stream)
btn_stop = tk.Button(button_frame, text="Stop Stream", command=stop_stream)
btn_exit = tk.Button(button_frame, text="Exit", command=root.quit)

btn_upload.pack(side=tk.LEFT, padx=5)
btn_start.pack(side=tk.LEFT, padx=5)
btn_stop.pack(side=tk.LEFT, padx=5)
btn_exit.pack(side=tk.LEFT, padx=5)

# Video display label with default size
video_label = tk.Label(root, width=800, height=600)
video_label.pack(expand=True, fill="both")


def update_frame():
    try:
        frame_data = frame_queue.get_nowait()
        image = Image.open(io.BytesIO(frame_data))
        # Determine current label size; use default size if too small
        current_width = video_label.winfo_width()
        current_height = video_label.winfo_height()
        default_width = 800
        default_height = 600
        target_width = current_width if current_width > 100 else default_width
        target_height = current_height if current_height > 100 else default_height
        resized_image = image.resize((target_width, target_height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image=resized_image)
        video_label.configure(image=photo)
        video_label.image = photo
    except queue.Empty:
        pass
    root.after(20, update_frame)


root.after(20, update_frame)
root.mainloop()
