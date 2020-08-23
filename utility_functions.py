import os
import pandas as pd
import glob

#This function merge the .csv files in the folder (accessed by the given 'path'). 
#.csv files are sorted based on the timestamps (time of creation/modification) before merging the files
def merge_meta_info(path,subset_type):
    
    os.chdir(path)

    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    all_filenames.sort(key=lambda x: os.path.getmtime(x))
    print(all_filenames)

    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
    #export to csv
    combined_csv.to_csv('word_metainfo_'+subset_type+'.csv', index=False, encoding='utf-8-sig')

    for filename in all_filenames:
        os.remove(filename) 