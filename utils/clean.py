import os
import shutil

def cleanup_model(speaker):
    try:
        # Delete multiple folders and their contents
        folder_paths = [
            f'configs/{speaker}',
            f'dataset/{speaker}',
            f'dataset_raw/{speaker}',
            f'filelists/{speaker}',
            f'long_dataset/{speaker}',
            f'separated/{speaker}',
            f'model/{speaker}/lightning_logs'
        ]
        for folder_path in folder_paths:
            try:
                shutil.rmtree(folder_path)
                print(f"Folder '{folder_path}' deleted successfully.")
            except FileNotFoundError:
                print(f"Folder '{folder_path}' does not exist.")

        # Delete files starting with "D_"
        file_folder = f'model/{speaker}'
        for file_name in os.listdir(file_folder):
            if file_name.startswith("D_"):
                file_path = os.path.join(file_folder, file_name)
                os.remove(file_path)
                print(f"File '{file_path}' deleted successfully.")

        # Delete a specific file
        file_path = f'model/{speaker}/G_0.pth'
        try:
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")
        except FileNotFoundError:
            print(f"File '{file_path}' does not exist.")

    except Exception as e:
        print('Error: ', e)

def cleanup_inference(audio_name):
    try:
        # Delete multiple folders and their contents
        folder_paths = [
            f'separated/{audio_name}',
            f'inference/{audio_name}',
            f'results/{audio_name}',
        ]
        for folder_path in folder_paths:
            try:
                shutil.rmtree(folder_path)
                print(f"Folder '{folder_path}' deleted successfully.")
            except FileNotFoundError:
                print(f"Folder '{folder_path}' does not exist.")

    except Exception as e:
        print('Error: ', e)
