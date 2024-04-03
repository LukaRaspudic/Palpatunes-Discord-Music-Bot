FROM python:latest
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install --no-cache-dir discord.py
RUN pip install --no-cache-dir yt-dlp
RUN pip install --no-cache-dir discord.py pynacl
RUN apt-get update && apt-get install -y ffmpeg
CMD ["python", "Palpatunes.py"]