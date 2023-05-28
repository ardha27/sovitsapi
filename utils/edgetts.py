import subprocess
import audiosegment
from pydub import AudioSegment
from utils.inference import *

def edgetts(speaker, text):
    try:
        command = ['edge-tts', '--voice', 'id-ID-GadisNeural', '--text', text, '--write-media', 'tts/edge.mp3']
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        print(result.stdout)

        audio = audiosegment.from_file("tts/edge.mp3")

        # Set the output format to WAV
        audio = audio.set_sample_width(2)
        audio = audio.set_frame_rate(44100)
        audio = audio.set_channels(1)

        # Export the audio to WAV format
        audio.export("tts/edge-conv.wav", format='wav')

        command = f"svc infer tts/edge-conv.wav -c model/{speaker}/config.json -m model/{speaker}/{speaker}.pth -o tts/result.wav"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())

        audio = AudioSegment.from_wav('tts/result.wav')
        audio.export('tts/result.mp3', format='mp3')

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    edgetts("pina", "halo kawan kawan, apa kabar semuanya?")