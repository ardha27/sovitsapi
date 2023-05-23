import requests

audio_file_path = "./Drake.wav"
url = 'https://jibril-gudal--test-app-training.modal.run'
speaker = 'Drake'
epochs = 100
batch_size = 16

files = {
    'audio': open(audio_file_path, 'rb')
}

data = {
    'speaker': speaker,
    'epochs': str(epochs),
    'batch_size': str(batch_size)
}

response = requests.post(url, files=files, data=data)

print(response.json())
