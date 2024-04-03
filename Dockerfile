FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install --no-cache-dir discord.py
RUN pip install --no-cache-dir yt-dlp
RUN pip install --no-cache-dir discord.py pynacl
RUN pip install --no-cache-dir ffmpeg
CMD ["python", "Palpatunes.py"]