import asyncio
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from queue import Queue
import soundfile as sf
import uvicorn
import os
import datetime
import glob
from pydub import AudioSegment
from utils.youtube import *
from utils.demucs import *
from utils.model_data import *
from utils.split import *
from utils.training import *
from utils.clean import *
from utils.inference import *
from utils.combine import *

app = FastAPI()
request_queue = Queue()

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
async def training(background_tasks: BackgroundTasks, audio: UploadFile = File(None), speaker: str = Form(...), youtube_link: str = Form(None), epochs: int = Form(...), batch_size: int = Form(...)):
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
            audio = AudioSegment.from_file(audio.file)
            audio.export(f"{speaker_dir}/audio.wav", format="wav")

        elif youtube_link is not None:
            download_from_url("training", youtube_link, speaker)

        else:
            return {"message": "Either 'audio' or 'youtube_link' must be provided."}
        
        audio_file = f"{speaker_dir}/audio.wav"
        data, sample_rate = sf.read(audio_file)
        duration = len(data) / sample_rate

        # Separate the audio
        speaker_id = sovits_data(speaker, duration, "Separating Vocal From Noise")
        background_tasks.add_task(separate_audio, "training", speaker)

        # Split the audio
        background_tasks.add_task(update_status, speaker_id, "Splitting Audio")
        background_tasks.add_task(split_audio, speaker)

        # Training
        background_tasks.add_task(update_status, speaker_id, "Training")
        background_tasks.add_task(training_sovits, speaker, epochs, batch_size)
        background_tasks.add_task(cleanup_model, speaker)

        folder_path = f"model/{speaker}"

        # Find all .pth files in the folder
        file_paths = glob.glob(os.path.join(folder_path, "*.pth"))

        # Filter the file paths to get only .pth files
        filtered_file_paths = [path for path in file_paths if os.path.isfile(path)]

        # Check if only one .pth file exists
        if len(filtered_file_paths) == 1:
            background_tasks.add_task(update_status, speaker_id, "Model Ready")
        else:
            background_tasks.add_task(update_status, speaker_id, "Error Occurred during Training")

        response = {
            "message": "Data will be processed",
            "speaker_id": speaker_id,
            "speaker": speaker
        }

        return response
    
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
        audio = AudioSegment.from_file(audio.file)
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

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
