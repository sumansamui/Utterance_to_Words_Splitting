
# Project: Utterance to word Splitting 


This project develops a new database (containing audio files with a single word in it) from a standard speech corpus. So, the python scripts (in this repository) take an speech corpus (e.g. LibriSpeech) and split the audio files (containing utterances) into audio files (each containing a single word). Hence, the output of the scripts will audio files corresponding to one word per file.

## General steps to be followed:

* Run Google cloud speech-to-text or any standard ASR API on the speech corpus

* Calculate the utterance level WER by comparing the obtained hypothesis with the available ground-truth transcript.

    If WER==0:
  1. Perform utterance-to-word trimming based on time-tags
  2. Store the meaningful meta-Info from the original dataset, such as speaker ID, speaker gender, etc.

## Possible challenges

* For most spoken languages, the boundaries between lexical units are difficult to identify. There is hardly any pauses in between two words.

* Inter-word spaces used by many written languages, would rarely correspond to pauses in their spoken version. Only in case of very slow speech, the speaker deliberately inserts those pauses.

* In normal speech, one typically finds many consecutive words being said with no pauses between them, and often the final sounds of one word blend smoothly or fuse with the initial sounds of the next word (Co-articulation effect).

## Instruction to the LibriSpeech users:


1. The script is by default written for LibriSpeech corpus. If you want to use some other corpus,
   please check config.py and instructions given below

2. Set the LibriSpeech corpus path in config.py

3. Set the path of Google-API key which is required to run Google Cloud ASR.

4. Use the conda environment: environment_utt_to_words.yaml and then run the top-level script main_utt_to_words.py

  $ conda env create -f environment_utt_to_words.yaml

  $ source activate utterance_to_word

  $ python3 main_utt_to_words.py 

## Instruction to the users who want to use corpus other than LibriSpeech:


1. First of all, set the path_to_corpus in config.py

2. Set the speaker_meta_info_file_name and path of the same in config.py.

3. Set the path of Google-API key (in config.py) which is required to run Google Cloud ASR.

4. There are two customized functions in corpus_functions.py, namely extract_reference_transcript
   and find_speaker_gender. You need to modify them as per corpus requirement.
   
5. If the file-formats and sampling rate of the audio files in your corpus  are different from LibriSpeech,
   then please change the following portion in run_ASR method in transcribe.py:
       config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_word_time_offsets=True)
        
### For queries and further information:

please contact: samuisuman@gmail.com
 
### Copyright (c) by Suman Samui