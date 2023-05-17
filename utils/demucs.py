import subprocess

def separate_audio(mode, speaker):
    try:
        if mode == 'training':
            command = f"demucs --two-stems=vocals -o separated/{speaker} long_dataset/{speaker}/audio.wav"
        elif mode == 'inference':
            command = f"demucs --two-stems=vocals -o separated/{speaker} inference/{speaker}/audio.wav"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())
    except Exception as e:
        print("Error: ", e)