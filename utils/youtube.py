import yt_dlp

def download_from_url(mode, url, audio_name):
    if mode == 'training':
        output = f'long_dataset/{audio_name}/audio'
    elif mode == 'inference':
        output = f'inference/{audio_name}/audio'

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        "outtmpl": f'{output}',  # this is where you can edit how you'd like the filenames to be formatted
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info_dict = ydl.extract_info(url, download=False)
        filename = ydl.prepare_filename(info_dict)
        return filename

