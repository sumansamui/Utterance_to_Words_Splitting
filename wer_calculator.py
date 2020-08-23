#This package contains function related to WER calculation
#The Reference and Hypothesis are processed to normalize WER

import re 
import inflect
from jiwer import wer


def wer_calc(ref,hyp):
    ref=process_string(ref)
    hyp=process_string(hyp)
    return wer(ref,hyp)

def process_string(s):
    s=s.upper()
    s=s.replace('.','')
    s=s.replace(',','')
    abbr_dict={
    'MR':'MISTER',
    'APPROX':'APPROXIMATELY',
    'APPT': 'APPOINTMENT',
    'ASAP': 'AS SOON AS POSSIBLE',
    'C/O':'CARE OF',
    'EST':'ESTABLISHED',
    'MIN':'MINIMUM',
    'MISC':'MISCELLANEOUS',  
    'VS':'VERSUS',
    'MRS':'MISTRESS',
    'NO': 'NUMBER',
    'AVE': 'AVENUE',
    'DR': 'DOCTOR',
    'LN': 'LANE',
    'DR': 'DOCTOR',
    'RD': 'ROAD', 
    'ST': 'STREET',
    'PH': 'PHONE',
    'DIST':'DISTRICT',
    'ETC':'ET CETERA',
    'TEL':'TELEPHONE',
    'TEMP':'TEMPERATURE',
    'MON':'MONDAY',
    'TUE':'TUESDAY',
    'WED':'WEDNESDAY',
    'THU':'THRUSDAY',
    'FRI':'FRIDAY',
    'SAT':'SATURDAY',
    'SUN':'SUNDAY',
    'JAN':'JANUARY',
    'FEB':'FEBRUARY',
    'MAR':'MARCH',
    'APR':'APRIL',
    'JUN':'JUNE',
    'JUL':'JULY',
    'AUG':'AUGUST',
    'SEP':'SEPTEMBER',
    'OCT':'OCTOBER',
    'NOV':'NOVEMBER',
    'DEC':'DECEMBER',
    'E':'EAST',
    'N':'NORTH',
    'W':'WEST',
    'S':'SOUTH',
    'NW':'NORTH-WEST',
    'NE':'NORTH-EAST',
    'SW':'SOUTH-WEST',
    'SE':'SOUTH-EAST'}
    array = getNumbers(s)  
    s=replace_numbers(s,array)
    # Removing hyphens from the string
    s=s.replace('-',' ')
    s=expand_abbreviation(s,abbr_dict)
    #print(s)
    return s

# Function to extract all the numbers from the given string 
def getNumbers(s): 
    array = re.findall(r'[0-9]+', s) 
    return array 

def replace_numbers(s,array): 

    if len(array) == 0:
        #print('the list is empty')
        pass

    else:    
        p = inflect.engine()
        p.number_to_words(array[0])

        for i in range(0,len(array)):

            s=s.replace(array[i],p.number_to_words(array[i]))
    s=s.upper()
    return s    


def expand_abbreviation(s,abbr_dict):
    
    words=s.split(' ')

    for n,w in enumerate(words):
        for i in abbr_dict.keys():
            if w==i:
                words[n]=abbr_dict[i]
    s=' '.join(words)
    return s   