FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN ["apt", "update"]
RUN ["apt", "install", "-y", "build-essential"]
RUN ["pip", "install", "-U", "pip", "setuptools", "wheel"]
RUN ["pip", "install", "-U", "so-vits-svc-fork"]
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]