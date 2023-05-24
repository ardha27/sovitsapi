from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from modal import Image, Stub, asgi_app, SharedVolume
import soundfile
import os
import datetime
import glob
import pydub
from utils.youtube import *
from utils.demucs import *
from utils.model_data import *
from utils.split import *
from utils.training import *
from utils.clean import *
from utils.inference import *

stub = Stub("Test_App")
app = FastAPI()
volume = SharedVolume().persist("doc_ocr_model_vol")
CACHE_PATH = "/root/model_cache"

image = (
    Image.debian_slim().apt_install("curl").run_commands(
        "apt-get update -y && apt-get install -y git",
        "apt install ffmpeg -y",
        "pip install -U demucs",
        "pip install -U pip setuptools wheel",
        "pip install torch torchvision torchaudio",
        "pip install -U git+https://github.com/voicepaw/so-vits-svc-fork.git",
        "pip install -U fastapi librosa numpy pydub SoundFile python-multipart uvicorn yt_dlp"
    )
)   

@stub.function(image=image, gpu="any", shared_volumes={CACHE_PATH: volume})
def training_process(speaker, audio, youtube_link, epochs, batch_size):

    # Create the directory for the speaker if it does not exist
    speaker = speaker.replace(" ", "_")

    current_time = datetime.datetime.now()
    unique_filename = current_time.strftime("%Y%m%d%H%M%S")
    speaker = speaker + "_" + unique_filename

    speaker_dir = f"long_dataset/{speaker}"
    if not os.path.exists(speaker_dir):
        os.makedirs(speaker_dir)

    if audio is not None:
        # Convert the audio data to WAV format
        audio = pydub.AudioSegment.from_file(audio.file)
        audio.export(f"{speaker_dir}/audio.wav", format="wav")

    elif youtube_link is not None:
        download_from_url("training", youtube_link, speaker)

    else:
        return {"message": "Either 'audio' or 'youtube_link' must be provided."}
    
    audio_file = f"{speaker_dir}/audio.wav"
    data, sample_rate = soundfile.read(audio_file)
    duration = len(data) / sample_rate

    # Separate the audio
    speaker_id = sovits_data(speaker, duration, "Separating Vocals")
    separate_audio("training", speaker)
    
    # Split the audio
    update_status(speaker_id, "Splitting Audio")
    split_audio(speaker)

    # Training
    update_status(speaker_id, "Training")
    training_sovits(speaker, epochs, batch_size)
    cleanup_model(speaker_id, speaker)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/all")
def get_database():
    with open("database.json", "r") as file:
        database_content = json.load(file)
    return database_content

@app.get("/id/{speaker_id}")
def get_speaker_by_id(speaker_id: int):
    with open("database.json", "r") as file:
        database_content = json.load(file)

    filtered_data = [data for data in database_content if data["id"] == speaker_id]

    if filtered_data:
        return filtered_data[0]
    else:
        return {"message": "Speaker not found"}
    
@app.post("/training")
async def training(audio: UploadFile = File(None), speaker: str = Form(...), youtube_link: str = Form(None), epochs: int = Form(...), batch_size: int = Form(...)):
    
    call = training_process.spawn(speaker, audio, youtube_link, epochs, batch_size)

    return {"call_id": call.object_id}
    
@app.post("/inference")
async def inference(background_tasks: BackgroundTasks, speaker_id: int = Form(...), audio: UploadFile = File(None), audio_name: str = Form(...), youtube_link: str = Form(None), pitch: int = Form(...)):
    
    audio_name = audio_name.replace(" ", "_")

    current_time = datetime.datetime.now()
    unique_filename = current_time.strftime("%Y%m%d%H%M%S")
    audio_name = audio_name + "_" + unique_filename

    audio_dir = f"inference/{audio_name}"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    if audio is not None:

        # Convert the audio data to WAV format
        audio = pydub.AudioSegment.from_file(audio.file)
        audio.export(f"{audio_dir}/audio.wav", format="wav")

    elif youtube_link is not None:
        download_from_url("inference", youtube_link, audio_name)

    else:
        return {"message": "Either 'audio' or 'youtube_link' must be provided."}
    
    # Separate the audio
    separate_audio("inference", audio_name)

    with open("database.json", "r") as file:
        database = json.load(file)

    speaker = ""
    for entry in database:
        if entry["id"] == speaker_id:
            speaker = entry["speaker"]

    folder_path = f"model/{speaker}"

    # Find all .pth files in the folder
    file_paths = glob.glob(os.path.join(folder_path, "*.pth"))

    # Filter the file paths to get only .pth files
    filtered_file_paths = [path for path in file_paths if os.path.isfile(path)]

    # Check if only one .pth file exists
    pth_file_path = ""
    if len(filtered_file_paths) == 1:
        pth_file_path = filtered_file_paths[0]
        print(f"Found .pth file: {pth_file_path}")
    else:
        print("Error: More than one .pth file or no .pth file found.")

    inference_sovits(speaker, audio_name, pth_file_path, pitch)

    def combine_audio(audio_name):
        try:
            VOCAL = f"results/{audio_name}/vocals.wav" #@param {type:"string"}
            INSTRUMENT = f"separated/{audio_name}/htdemucs/audio/no_vocals.wav" #@param {type:"string"}

            sound1 = pydub.AudioSegment.from_file(VOCAL)
            sound2 = pydub.AudioSegment.from_file(INSTRUMENT)

            combined = sound1.overlay(sound2)

            combined.export(f"results/{audio_name}/result.wav", format='wav')
        except Exception as e:
            print("Error: ", e)


    combine_audio(audio_name)
    
    # Path to the resulting audio file
    # result_audio_path = f"results/{audio_name}/result.wav"
    result_audio_path = f"results/{audio_name}/result.wav"

    background_tasks.add_task(cleanup_inference, audio_name)

    if os.path.isfile(result_audio_path):
    # Return the audio file as a response
        return FileResponse(result_audio_path)
    else:
        # If an audio file is not found, return an error message
        return {"message": "Error: Resulting audio file not found."}

@stub.function(image=image, gpu="any")
@asgi_app()
def fastapi_app():
    return app
