#This Package contains two customized functions for LibriSpeech Corpus
#If you want to use other corpus, then you have to write your functions

#This function extract the reference transcription from the lines of text based on the count value 
def extract_reference_transcript(lines_text,count):
    line = lines_text[count]
    line_wn = ''.join([i for i in line if not i.isdigit()])
    line_wh = line_wn.replace('-','')
    ref = line_wh.lstrip()
    return ref


#This function extract gender of the speaker from the speaker meta info file 
def find_speaker_gender(speaker_id,speaker_meta_file):
    with open(speaker_meta_file) as f:
        lines = f.readlines()
    meta_info_list = lines
    for line in meta_info_list:
        if speaker_id in line.split(' ')[0]:
            print(line)
            sl=line
            break
        else:
            pass
    gender=sl.partition('|')[2].partition('|')[0]  
    gender=gender.strip()
    return gender