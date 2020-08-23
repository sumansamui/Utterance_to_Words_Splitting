import io
import soundfile as sf
import os
import math
import sys
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types



def run_ASR(filename):
    #Google-Cloud Speech Recognizer
    """Transcribe the given audio file asynchronously and output the word time
    offsets."""
    client = speech.SpeechClient()
    # Loads the audio into memory
    with io.open(filename, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
        audio_file.close()
    
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_word_time_offsets=True)
    operation = client.long_running_recognize(config, audio)
    print('Waiting for operation to complete...')
    result = operation.result(timeout=1000)
    for result in result.results:
        alternative = result.alternatives[0]  
    return alternative