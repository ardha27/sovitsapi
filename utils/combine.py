from pydub import AudioSegment

def combine_audio(audio_name):
    try:
        VOCAL = f"results/{audio_name}/vocals.wav" #@param {type:"string"}
        INSTRUMENT = f"separated/{audio_name}/htdemucs/audio/no_vocals.wav" #@param {type:"string"}

        sound1 = AudioSegment.from_file(VOCAL)
        sound2 = AudioSegment.from_file(INSTRUMENT)

        combined = sound1.overlay(sound2)

        combined.export(f"results/{audio_name}/result.wav", format='wav')
    except Exception as e:
        print("Error: ", e)

      