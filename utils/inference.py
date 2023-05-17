import subprocess
from utils.model_data import *

def inference_sovits(speaker, audio, pth, pitch):
    try:
        command = f"svc infer separated/{audio}/htdemucs/audio/vocals.wav -c model/{speaker}/config.json -m {pth} -na -t {pitch} -o results/{audio}/vocals.wav"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())

    except Exception as e:
        print("Error:", e)