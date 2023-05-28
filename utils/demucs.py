import subprocess

def separate_audio(speaker):
    try:
        command = f"demucs --two-stems=vocals -o separated/{speaker} inference/{speaker}/audio.wav"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())
    except Exception as e:
        print("Error: ", e)