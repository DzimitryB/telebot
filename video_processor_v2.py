from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import yt_dlp
import whisper
import torch

# Настраиваем устройство
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Whisper использует устройство: {device}")

# Load the Whisper model with explicit device mapping
try:
    model = whisper.load_model("base")
    model.to(device)  # Explicitly move the model to the MPS device
    print("Model successfully loaded and moved to:", device)
except Exception as e:
    print(f"Error loading model: {e}")

# Инициализация FastAPI
app = FastAPI()

# Модель для передачи данных через запрос
class VideoURL(BaseModel):
    url: str

# Функция загрузки аудио или низкого разрешения видео
def download_audio_or_low_res_video(url, output_path="output"):
    ydl_opts = {
        'format': 'bestaudio/best[height<=144]', 
        'outtmpl': f'{output_path}.%(ext)s',
        'quiet': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.mp4', '.mp3')
            return audio_file
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке: {e}")

# Функция для транскрипции аудио
def transcribe_audio(audio_path):
    try:
        result = model.transcribe(audio_path)
        os.remove(audio_path)  # Удаляем временный файл
        return result["text"]
    except Exception as e:
        raise RuntimeError(f"Ошибка при обработке аудио: {e}")

# Эндпоинт для обработки видео
@app.post("/transcribe/")
def transcribe_video(video_url: VideoURL):
    """
    Обрабатывает видео по переданному URL и возвращает текст.
    """
    try:
        # Шаг 1: Загрузка аудио
        audio_file = download_audio_or_low_res_video(video_url.url)
        # Шаг 2: Распознавание текста
        transcript = transcribe_audio(audio_file)
        return {"status": "success", "transcription": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))