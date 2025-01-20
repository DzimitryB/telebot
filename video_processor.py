import os
import yt_dlp
import whisper
import torch

# Инициализация модели Whisper
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Whisper использует устройство: {device}")  
model = whisper.load_model("base", device=device) # Используйте "medium" или "large" для большей точности, если требуется.


# Функция для загрузки только аудио или минимального объема видео
def download_audio_or_low_res_video(url, output_path="output"):
    """
    Загружает только аудио или минимальное видео (144p), чтобы уменьшить объем данных.
    """
    ydl_opts = {
        'format': 'bestaudio/best[height<=144]',  # Предпочитается аудио, если есть, иначе минимальное разрешение
        'outtmpl': f'{output_path}.%(ext)s',     # Генерация имени файла
        'quiet': True,                           # Отключение логов
        'postprocessors': [
            {  # Преобразование в аудио
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

# Функция для распознавания текста из аудио
def transcribe_audio(audio_path):
    """
    Распознает текст из аудиофайла с использованием Whisper.
    """
    try:
        result = model.transcribe(audio_path)
        os.remove(audio_path)  # Удаляем временный аудиофайл
        return result["text"]
    except Exception as e:
        raise RuntimeError(f"Ошибка при обработке аудио: {e}")

# Тестирование функций (опционально)
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=your_video_url"
    try:
        print("Загружаю только аудио...")
        audio_file = download_audio_or_low_res_video(test_url)
        print(f"Файл {audio_file} загружен. Распознаю текст...")
        transcript = transcribe_audio(audio_file)
        print("Распознанный текст:")
        print(transcript)
    except Exception as e:
        print(f"Ошибка: {e}")