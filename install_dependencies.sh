#!/bin/bash

apt-get update -y
apt install ffmpeg -y
pip install -U demucs
pip install -U pip setuptools wheel
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -U so-vits-svc-fork
pip install -r requirements.txt