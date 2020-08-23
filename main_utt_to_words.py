import sys
import os
import config
from glob import glob
import pandas as pd
from corpus_functions import extract_reference_transcript,find_speaker_gender
from audio_transcribe import run_ASR
from wer_calculator import wer_calc
from utility_functions import merge_meta_info
from audio_splitting import utt_to_words_splitting


print('Welcome to utterance-to-words-splitting setup')
print('By default, the script is written for LibriSpeech corpus.') 
print('If you wish to use other corpus, please refer to README.txt file') 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=config.path_to_google_api_key

#Folder_paths hold the paths of each of the subset-type (such as dev-clean, train-clean-100,...so on) inside the path_to_corpus
folder_paths = sorted(glob(config.path_to_corpus+'/*/'))

folder_name_list=[]
for paths in folder_paths:
    folder_name=os.path.basename(os.path.normpath(paths))
    folder_name_list.append(folder_name)
    
print('The following subset-types of LibriSpeech are available') 
print(folder_name_list)

#It would ask the user to select a particular subset
path_select=input('Please select a subset:')

#Then it would check whether the given subset is valid or not
for paths in folder_name_list:
    if path_select==paths:
        print('You have selected a valid subset!')
        break

subset_type=path_select
path_to_subset=os.path.join(config.path_to_corpus,subset_type)

#SPEAKERS.TXT in libri-speech file contains speaker information such as name, gender etc. Each subset folder in Librispeech contain a SPEAKERS.TXT file.
path_to_speaker_meta_info=os.path.join(path_to_subset,config.speaker_meta_info_file_name)

#This would set the path of audio files (utterances) from different speakers within a selected subset
path_to_subset_audio=os.path.join(path_to_subset,subset_type)

#It would give the paths of each speaker within a subset
speaker_paths=sorted(glob(path_to_subset_audio+'/*/'))

speaker_id_list=[]
for paths in speaker_paths:
    folder_name=os.path.basename(os.path.normpath(paths))
    speaker_id_list.append(folder_name)
    
print(subset_type + ' contains the following speaker sets')
print(speaker_id_list)

#This would ask the user to select a set of speakers within the subset     
selected_speaker_list=input("Please give coma-separated speaker ids or type 'all' if you want to select all speakers within the subset:")
selected_speaker_id_list=selected_speaker_list.split(',')

#This would check the validity of the given speaker list by user
if selected_speaker_id_list[0]=='all':
    selected_speaker_id_list=speaker_id_list
    print('You have selected all speaker-ids!')
else:
    count=0
    for speaker_id in speaker_id_list:
        for speaker in selected_speaker_id_list:
            if speaker==speaker_id:
                count +=1
    if count==len(selected_speaker_id_list) :
        print('You have selected all valid speaker-ids!')
    else:
        print('You have selected invalid speaker-id!')
        sys.exit("Try again!")
        


print('The utterance to words splitting process has been started.') 
print('Please check the log file and output folders once the program execution is done.')
#Empty lists are initialized meta-data records
filename_list=[]
subset_list=[]
speaker_id_list=[]
chapter_id_list=[]
segment_id_list=[]
gender_list=[]
ref_list=[]
hyp_list=[]
wer_list=[]

path_to_output=config.output_folder + subset_type


os.makedirs(config.path_to_log_file,exist_ok=True)
sys.stdout=open(os.path.join(config.path_to_log_file,'log_'+ subset_type+'.txt'),"w")
for speaker_id in selected_speaker_id_list:
    path_to_speaker_id=os.path.join(path_to_subset_audio,speaker_id)
    gender=find_speaker_gender(speaker_id,path_to_speaker_meta_info)
    print(path_to_speaker_id)
    path_to_chapters=sorted(glob(path_to_speaker_id+'/*/'))
    #print(path_to_chapters)
    for i in range(0,len(path_to_chapters)):
        for filename in sorted(os.listdir(path_to_chapters[i])):
            if filename.endswith('.txt'):
                transcript_file=filename
                print(transcript_file)
                print(path_to_chapters[i])
                with open(os.path.join(path_to_chapters[i],transcript_file)) as f:
                     gt_transcripts = f.readlines()
                print('Reading transcript.....')   
                count=0
        for filename in sorted(os.listdir(path_to_chapters[i])):
            chapter_id = os.path.basename(os.path.normpath(path_to_chapters[i]))
            if filename.endswith('.flac'):
                segment_id=os.path.splitext(filename)[0][-4:]
                print('Reading the file:'+ filename)
                print('Speaker_id:'+speaker_id)
                print('Chapter_id:'+chapter_id)
                print('Segment_id:'+segment_id)
                print('Subset-type:'+ subset_type)
                #Extracting REFERENCE
                ref = extract_reference_transcript(gt_transcripts,count)
                print('REF:'+ref.upper())
                #Getting HYPOTHESIS by passing the filepath to Google-Cloud ASR   
                hypothesis=run_ASR(os.path.join(path_to_chapters[i],filename))
                hyp=hypothesis.transcript
                print('HYP:'+hyp.upper())
                #Determining WER
                wer_value=wer_calc(ref,hyp)
                print('WER:'+str(wer_value))
                count +=1 
                #Performing Utterance to Words Splitting when WER equals to zero
                if  wer_value != 0:
                    print('Since WER='+ str(wer_value) + ',skipping utterance to word conversion!')
                else:
                    print('Starting utterance to word conversion!')
                    utt_to_words_splitting(os.path.join(path_to_chapters[i],filename),subset_type,
                                           hypothesis,path_to_output,config.path_to_word_meta_info,path_to_speaker_meta_info)
            
            
                filename_list.append(filename)
                subset_list.append(subset_type)
                speaker_id_list.append(speaker_id)
                chapter_id_list.append(chapter_id)
                segment_id_list.append(segment_id)
                gender_list.append(gender)
                ref_list.append(ref)
                hyp_list.append(hyp.upper())
                wer_list.append(wer_value)
                
df = pd.DataFrame({'Filename':filename_list, 'Subset-type':subset_list,'Speaker-ID':speaker_id_list,
                   'Chapter-ID':chapter_id_list,'Segment-ID':segment_id_list,'Gender':gender_list,
                   'Ref_trans.':ref_list, 'Hyp_trans.':hyp_list, 'WER':wer_list})
            
                 
print('Writing to meta-info in the .csv file...')
os.makedirs(config.path_to_utt_meta_info,exist_ok=True)
df.to_csv(os.path.join(config.path_to_utt_meta_info,'utterance_level_meta_info_'+subset_type+'.csv'), index=False)

print('Merging word meta-info (.csv) files...')
merge_meta_info(config.path_to_word_meta_info,subset_type)
print('Utterance to words splitting done!')
sys.stdout.close()