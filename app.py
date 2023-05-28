from fastapi import FastAPI, File, Form, BackgroundTasks, UploadFile
from fastapi.responses import FileResponse
import os
import uvicorn
import datetime
import threading
from pyngrok import ngrok
from utils.ytdownload import *
from utils.demucs import *
from utils.combine import *
from utils.clean import *
from utils.inference import *
from utils.ytsearch import *
from utils.transcribe import *
from utils.edgetts import *

app = FastAPI()

def ngrok_api():
    ngrok_tunnel = ngrok.connect(8000)
    print("Public URL:", ngrok_tunnel.public_url)
    ngrok_process = ngrok.get_ngrok_process()
    try:
        # Block until CTRL-C or some other terminating event
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print(" Shutting down server.")
        ngrok.kill()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/whisper")
async def transcribe_audio(audio: UploadFile = File(...)):

    os.makedirs("transcribe", exist_ok=True)
    with open("transcribe/audio.mp3", 'wb') as file:
        file.write(await audio.read())

    result = transcribe("transcribe/audio.mp3")
    return {"message": result}

@app.post("/tts")
async def tts(speaker: str = Form(...), text: str = Form(...)):
    edgetts(speaker, text)
    result_audio_path = "tts/result.wav"
    return FileResponse(result_audio_path)

@app.post("/inference")
async def inference(background_tasks: BackgroundTasks, speaker: str = Form(...), song: str = Form(...)):
    
    current_time = datetime.datetime.now()
    audio_name = current_time.strftime("%Y%m%d%H%M%S")

    audio_dir = f"inference/{audio_name}"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    youtube_link, duration = ytsearch(song)

    if duration > 300:
        edgetts(speaker, "Maaf, lagu yang direquest melebihi 5 menit, silahkan request lagu lainnya")
        result_audio_path = "tts/result.wav"
        return FileResponse(result_audio_path)

    download_from_url(youtube_link, audio_name)
    
    separate_audio(audio_name)

    inference_sovits(speaker, audio_name)

    combine_audio(audio_name)
    
    result_audio_path = f"results/{audio_name}/result.wav"

    background_tasks.add_task(cleanup_inference, audio_name)

    if os.path.isfile(result_audio_path):
    # Return the audio file as a response
        return FileResponse(result_audio_path)
    else:
        # If an audio file is not found, return an error message
        return {"message": "Error: Resulting audio file not found."}
    
if __name__ == "__main__":
    public_url = threading.Thread(target=ngrok_api)
    public_url.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)