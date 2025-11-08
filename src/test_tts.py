from tts_service import tts_service

# Test tiếng Việt
text_vi = "Xin chào, đây là tin nhắn thử nghiệm."
audio_path = tts_service.text_to_speech(text_vi, lang='vi')
if audio_path:
    print(f"Audio file created at: {audio_path}")
    print(f"Audio URL: {tts_service.get_audio_url(audio_path)}")
else:
    print("Failed to create audio file")