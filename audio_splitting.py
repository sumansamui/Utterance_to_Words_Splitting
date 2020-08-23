#This package contains functions to split utterance into words 
import math
import soundfile as sf
import numpy as np
import os
import pandas as pd
from corpus_functions import extract_reference_transcript,find_speaker_gender


#This is the main-level function to splitt the utterance into words
def utt_to_words_splitting(filename,subset_type,hypothesis,path_to_output,path_to_word_meta_info,speaker_meta_file):
    
    filename_list=[]
    word_list=[]
    speaker_id_list=[]
    chapter_id_list=[]
    segment_id_list=[]
    gender_list=[]
    time_tag_list=[]
    subset_type_list=[]
    norm_factor_list=[]
    
    os.makedirs(path_to_output,exist_ok=True)
    os.makedirs(path_to_word_meta_info,exist_ok=True) 
    utt_id=os.path.basename(os.path.normpath(filename))
    utt_id_we=os.path.splitext(utt_id)[0]
    speaker_id=utt_id_we.split('-')[0]
    chapter_id=utt_id_we.split('-')[1]
    segment_id=utt_id_we.split('-')[2]
    gender=find_speaker_gender(speaker_id,speaker_meta_file)
    
    for word_info in hypothesis.words:
        word = word_info.word
        start_time = word_info.start_time
        end_time = word_info.end_time
        print('Word: {}, start_time: {}, end_time: {}'.format(word,
                start_time.seconds + start_time.nanos * 1e-9,
                end_time.seconds + end_time.nanos * 1e-9))
        s=start_time.seconds + start_time.nanos * 1e-9
        e=end_time.seconds + end_time.nanos * 1e-9
        data, samplerate = sf.read(filename)
        word_data = data[math.floor(s*samplerate):math.ceil(e*samplerate)]
        
        wtg=[s,e]
        
        valid_status=word_validity_check(data,s,e,samplerate,20,10)
        
       
    
        if valid_status==True:
            print(str(word)+' has gained valid status!')
            l=len(os.listdir(path_to_output))
            word_file_name=str(l+1).zfill(4)
                        
            [word_data_n,norm_factor]=normalized_by_rms(data,word_data)
            AL=round(abs((e-s)/8), 2)
            word_data_p=padding_min_front_back(word_data_n,samplerate,AL)
            sf.write(os.path.join(path_to_output,word_file_name +'.flac'),word_data_p, samplerate)
            
            filename_list.append(str(word_file_name)+'.flac')
            word_list.append(word)
            speaker_id_list.append(speaker_id)
            chapter_id_list.append(chapter_id)
            segment_id_list.append(segment_id)
            gender_list.append(gender)
            time_tag_list.append(wtg)
            subset_type_list.append(subset_type)
            norm_factor_list.append(norm_factor)
            
        else:
            print(str(word)+' has failed to gain valid status!')
            
    df = pd.DataFrame({'Filename':filename_list,'Key':word_list, 'Subset-type':subset_type_list,'Speaker-ID':speaker_id_list,
                   'Chapter-ID':chapter_id_list,'Segment-ID':segment_id_list,'Gender':gender_list,
                   'Time-tag':time_tag_list, 'Norm-factor':norm_factor_list})
            
                
            
    df.to_csv(os.path.join(path_to_word_meta_info,'word_meta_info_'+str(utt_id_we)+'.csv'), index=False)
    

#This function checks the validity of word boundaries of a word (starting and ending). 
#In other words, it checks whether the word-boundary is in silence or not.
def word_validity_check(data,s,e,samplerate,T,win_size):
    if s==e:
        valid_status=False
    else:
        rms=compute_rms(data)
        data_n=data/rms
        Thr=compute_threshold(rms,T)
        vad=vad_rms(data,Thr)
        s_status=valid_word_boundary(s,data,vad,samplerate,win_size)
        if s_status==True:
            e_status=valid_word_boundary(e,data,vad,samplerate,win_size)
        else:
            print('skipping the end-point status check! proceeding to the next word...')
        
        if s_status==True and e_status==True:
            valid_status=True
        else:
            valid_status=False
    return valid_status
    
#This is a function to do RMS level normalization.
def normalized_by_rms(data,word_data):
    rms=compute_rms(data)
    word_data_n=word_data/rms
    word_data_n=word_data_n/max(abs(word_data_n))
    print('rms:',rms)
    return [word_data_n,rms]

#This function is to compute RMS level of wave 
def compute_rms(samples):
    N=len(samples)
    sum=0
    for x in samples:
        sum +=abs(x)**2
    rms=math.sqrt(sum/N)
    return rms
#This function is used to get Threshold level    
def compute_threshold(rms,T):
    rms_dB=10*math.log10(rms)
    Thr_dB=(rms_dB-T)
    Thr=math.pow(10,Thr_dB/10)
    return Thr
#This function is used to generate samplewise VAD
def vad_rms(samples,Thr):
    is_speech=[]
    for i in samples:
        if i>Thr:
            is_speech.append(1)
        else:
            is_speech.append(0)
    return is_speech
'''
This function takes word-boundary timestamp as an input and determine whether the word-boundary is in silence or not
The word boundary is in silence if the VAD based voting criterion, the following three criteria are satisfied:
1. VAD based voting criterion
2. STE (Short-time energy) criterion
3. ZCR (Zero crossing rate) criterion 
'''
def valid_word_boundary(timestamp,data,is_speech,samplerate,win_size):
    w=(win_size/2)
    if timestamp==0.0:
        ts=timestamp
        te=timestamp+win_size*1e-03
    else:
        ts=timestamp-w*1e-03
        te=timestamp+w*1e-03
        
    boundary_data=data[int(math.floor(ts*samplerate)):int(math.ceil(te*samplerate))]
    
    # VAD based voting criterion
    count=0
    for i in range(int(math.floor(ts*samplerate)),int(math.ceil(te*samplerate))+1):
        if is_speech[i]==0:
            count +=1
        else:
            pass
    total_samples_at_boundary=abs(int(math.ceil(te*samplerate))-int(math.floor(ts*samplerate)))
    if count>math.floor((total_samples_at_boundary)*0.5):
        print('count:'+str(count))
        print('Tot. samples at boundary:'+str(total_samples_at_boundary))
        vad_voting_silence=True
    else:
        vad_voting_silence=False

    # STE based criterion
    if vad_voting_silence==True:
        STEs=calculate_STE(data,samplerate,win_size)
        avg_STE=sum(STEs)/len(STEs)
        STE_wb=calculate_STE(boundary_data,samplerate,win_size)
        STE_wb=STE_wb[0]
    
        if STE_wb<avg_STE:
            print('STE @ boundary is less than avg. STE across the word time-interval')
            print('STE_wb:',STE_wb)
            print('avg. STE:',avg_STE)
            low_STE=True
        
        else:
            low_STE=False
    
    # ZCR based criterion
    
        ZCRs=calculate_ZCR(data,samplerate,win_size)
        avg_ZCR=sum(ZCRs)/len(ZCRs)
        ZCR_wb=calculate_ZCR(boundary_data,samplerate,win_size)
        ZCR_wb=ZCR_wb[0]
    
        if ZCR_wb<avg_ZCR:
            print('ZCR @ boundary is less than avg. ZCR across the word time-interval')
            print('ZCR_wb:',ZCR_wb)
            print('avg. ZCR:',avg_ZCR)
            low_ZCR=True
        
        else:
            low_ZCR=False
            
    else:
        print('Skipping STE and ZCR calculation')
        
    if vad_voting_silence==True and low_STE==True and low_ZCR==True:
        print('3 criterion are satisfied for the word-boundary')
        valid_wb=True
    else:
        valid_wb=False
        
    return valid_wb

#This function is used to calculate short-time energy
def calculate_STE(data,samplerate,frame_size):
    sampsPerMilli = int(samplerate / 1000)
    sampsPerFrame = sampsPerMilli * frame_size
    nFrames = int(len(data) / sampsPerFrame)
    STEs = []                                      # list of short-time energies
    for k in range(nFrames):
        startIdx = k * sampsPerFrame
        stopIdx = startIdx + sampsPerFrame
        window = np.zeros(data.shape)
        window[startIdx:stopIdx] = 1               # rectangular window
        STE = sum((data** 2)*(window**2))
        STEs.append(STE)
    return STEs

#This function is used to calculate Zero-crossing rate
def calculate_ZCR(data,samplerate,frame_size):
    sampsPerMilli = int(samplerate / 1000)
    sampsPerFrame = sampsPerMilli * frame_size
    nFrames = int(len(data) / sampsPerFrame)

    DC = np.mean(data)
    newSignal = data - DC

    ZCCs = []                                      # list of short-time zero crossing counts
    for i in range(nFrames):
        startIdx = i * sampsPerFrame
        stopIdx = startIdx + sampsPerFrame
        s = newSignal[startIdx:stopIdx]            
        ZCC = 0
        for k in range(1, len(s)):
            ZCC += 0.5 * abs(np.sign(s[k]) - np.sign(s[k - 1]))
        ZCCs.append(ZCC)
    return ZCCs

#This is function can be used padding a wave file
def padding_min_front_back(data,samplerate,AL):
    AL=AL/2
    zero_samples=math.floor(AL*samplerate)
    try:
        m = min(i for i in data if i > 0)
        print(m)
    except:
        m=0.0
        print(m)
    data=np.pad(data, (zero_samples,zero_samples), 'constant', constant_values=(m, m))
    #data=np.pad(data,(zero_samples,zero_samples),'edge')
    return data