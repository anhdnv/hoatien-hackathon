import os
from gtts import gTTS
import tempfile
import uuid
from pathlib import Path
from datetime import datetime
import time

class GTTSService:
    def __init__(self):
        # Sử dụng đường dẫn tuyệt đối
        self.audio_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "static" / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        print(f"TTS Service initialized using gTTS. Audio directory: {self.audio_dir}")
    
    def text_to_speech(self, text, speed: float = 2.0, lang: str = 'vi') -> str:
        """
        Chuyển đổi text thành speech sử dụng gTTS.
        Ghi chú: gTTS không hỗ trợ tham số 'speed' trực tiếp.
        
        Args:
            text (str): Văn bản cần chuyển đổi.
            speed (float): Tham số tốc độ (không được sử dụng trong gTTS nhưng được giữ lại cho tính tương thích).
            lang (str): Ngôn ngữ cho TTS (mặc định là tiếng Việt 'vi').
            
        Returns:
            str: Đường dẫn tuyệt đối đến file audio MP3 được tạo.
        """
        try:
            if not text:
                return None
            
            audio_filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            output_path = self.audio_dir / audio_filename
            
            tts = gTTS(text=text, lang=lang, slow=(speed < 1.0))
            
            # Lưu file audio
            tts.save(str(output_path))
            print(f"Audio đã được tạo: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            print(f"Lỗi trong text_to_speech (gTTS): {e}")
            return None
    
    def get_audio_url(self, audio_path: str) -> str:
        """Chuyển đổi đường dẫn file thành URL để frontend có thể truy cập"""
        if audio_path and os.path.exists(audio_path):
            static_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "static"
            relative_path = os.path.relpath(audio_path, str(static_dir))
            return f"/static/{relative_path.replace(os.sep, '/')}"
        return None
    
    def cleanup_old_audio(self, max_age_hours=24):
        """Dọn dẹp các file audio cũ hơn max_age_hours giờ."""
        try:
            now = time.time()
            cutoff_time = now - (max_age_hours * 3600)
            
            for file_path in self.audio_dir.glob("tts_*.mp3"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    print(f"Đã xóa file audio cũ: {file_path}")
        except Exception as e:
            print(f"Lỗi khi dọn dẹp audio files: {e}")

# Singleton instance
tts_service = GTTSService()