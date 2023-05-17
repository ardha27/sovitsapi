import subprocess
import json

def training_sovits(speaker, epochs):
    try:
        command = f"svc pre-resample -i dataset_raw/{speaker} -o dataset/{speaker}"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())

        command = f"svc pre-config -i dataset/{speaker} -c configs/{speaker}/config.json -f filelists/{speaker}"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())

        # Read the JSON data from the file
        with open(f'configs/{speaker}/config.json', 'r') as file:
            data = json.load(file)

        # Modify the value
        data['train']['epochs'] = epochs
        data['train']['batch_size'] = 5
        data['train']['keep_ckpts'] = 1

        # Write the updated data back to the file
        with open(f'configs/{speaker}/config.json', 'w') as file:
            json.dump(data, file, indent=4)

        command = f"svc pre-hubert -i dataset/{speaker} -c configs/{speaker}/config.json -fm dio"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        print(result.stdout.decode())

        command = f"svc train -c configs/{speaker}/config.json -m model/{speaker}"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, universal_newlines=True)

        for line in process.stdout:
            print(line, end='')

        process.wait()

    except Exception as e:
        print("Error:", e)

    