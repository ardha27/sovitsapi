#!/bin/bash

apt-get update -y
apt install ffmpeg -y
pip install -U demucs
pip install -U pip setuptools wheel
pip install -U openai-whisper
pip install -U youtube-search-python
pip install edge-tts
pip install -U so-vits-svc-fork
pip install -r requirements.txt