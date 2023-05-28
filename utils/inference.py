import subprocess

def inference_sovits(speaker, audio_name):
    try:
        command = f"svc infer separated/{audio_name}/htdemucs/audio/vocals.wav -c model/{speaker}/config.json -m model/{speaker}/{speaker}.pth -na -t 0 -o results/{audio_name}/vocals.wav"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())

    except Exception as e:
        print("Error:", e)