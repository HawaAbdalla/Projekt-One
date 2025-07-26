# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 06:58:58 2024

@author: PC
"""

#%%
def update_dataframe(csv,speeches_directory):
    """
    For this function to work, the file names need to be named as their titles. (See function sanitize_filename()).
    It matches the entries in the 'Title' column to the appropriate text files in the directory by their titles.
    
    Add a 'Minutes' column by processing the 'Length' column in csv file. This column will contain the minutes from 'Length' column.
    Add a 'Clean_Text' column by processing files with transcript in a directory. This column will contain paragraphs with stop words, special characters, etc. filtered out.
    Add a 'Transcript_Text' column by processing files. This column will contain only paragraphs from Donald Trump, e.g. no speaker stamp, no timestamp, no headers.  
    Add a 'POS_Tag' column by processing output from 'clean_text' function. This column will contain a dictionary with part of speech tags and their connected words. 
    
    Parameters
    ----------
    csv (str): Path to a csv file containing 'Title','Date', and 'Length' information about Trump speeches.
    speeches_directory (str): Path to directory containing transcript files with the titles as name.

    Returns
    -------
    trump_data (pd.DataFrame): Updated df with 'Minutes', 'Clean_Text', 'Transcript_Text' and 'POS_Tag' columns and row data.

    """
    
    # Load csv file into a pandas df
    trump_data = pd.read_csv(csv,encoding='utf-8')
    
    # Get all transcript text files in specified directory with os.listdir()
    # The Python os.listdir() method returns a list containing the names of the files within the given directory. / tutorialspoint.com
    speech_files = os.listdir(speeches_directory)
    
    # Add 'Minutes' column by subsetting information from 'Length' Column
    trump_data['Minutes'] = trump_data['Length'].str.split(':').str[0].astype(int)   # Splits values in column at ':'. Takes the first part [0], e.g. the minutes, and converts it to integer.
    
    trump_data['Clean_Text'] = ''   # Add 'Speech_Text' column
    trump_data['Transcript_Text'] = ''   # Add 'Transcript_Text' column
    trump_data['POS_Tag'] = ''   # Add a 'POS_Tag' column
    
    # Iterate over Dataframe rows
    for index,row in trump_data.iterrows():   # DataFrame.iterrows(): Iterate over DataFrame rows as (index, Series) pairs. / pandas.pydata.org
        title = row['Title'].lower()   # Assign data from 'Title' row to variable converting it to lowercase 
        matching_file = None   # Set 'matching_file' variable to value None
        
        # Iterate over files in directory with transcript files
        for file in speech_files:   
            if title in file.lower():   # If data from 'Title' row is in file, e.g. it is a match;
                matching_file = file   # Pair 'em!
                break
            
        if matching_file:   # If a matching file is found,
            file_path = os.path.join(speeches_directory,matching_file)   # Construct file path combining directory and the file in question
            clean_speech = clean_text(file_path)   # Calls clean_text() function to clean(!) text in speech file on the full file path
            dictionary = part_of_speech_tagging(clean_speech)   # Calls part_of_speech_tagging() function on the output from the function above to create a dictionary with part of speech tagging
            transcript_speech = transcript_text(file_path)   # Calls transcript_text() function to get paragraphs
            
            # pandas.DataFrame.at is used to access a single value for a row/column label pair. / pandas.pydata.org
            # Add the output from clean_text() function to the column at the current row[i]
            trump_data.at[index,'Clean_Text'] = clean_speech
            
            # Add the output from transcript_text() to the column at the current row[i]
            trump_data.at[index,'Transcript_Text'] = transcript_speech
            
            # Add output from part_of_speech_tagging() to the column at the current row[i]
            trump_data.at[index,'POS_Tag'] = dictionary
            
        else:   # Else, write error message to column at current row
            trump_data.at[index,'Speech_Text']=f'Clean text not found for {title}'
            trump_data.at[index,'Transcript_Text']=f'Transcript text not found for {title}'
            trump_data.at[index,'POS_Tag']=f'POS tagging failed for {title}'
            
    return trump_data   # Return the updated dataframe



#%%
def part_of_speech_tagging(clean_speech):
    """
    This function iterates over the output from function clean_text().
    
    The content is tokenized and tagged for part-of-speech.
    
    The result is then added to a dictionary with the grammatical categories as keys and words as values.
    No duplicates are added. 
    This dictionary is then returned and ready to be added to dataframe

    Parameters
    ----------
    clean_speech (str): Output string from the clean_text() function.

    Returns
    -------
    dictionary (dict): Dictionary with keys(categories) : values(words) .

    """
    
    dictionary=dict()   # Initialize dictionary
    words=word_tokenize(clean_speech)   # Tokenize the output from 'clean_text()' function
    result=nltk.pos_tag(words)   # Tag the tokenized words and assign to a results variable
    
    for word,tag in result:   # Iterate over word;tag pairs 
        if tag in dictionary:   # If tag (i.e. the key / POS tag) is in the dictionary
            if word not in dictionary[tag]:   # If word (i.e. value related to key) is not in the dictionary
                dictionary[tag].append(word)   # Append the word to the dictionary related to the appropriate tag
        else:
            dictionary[tag]=[word]
    
    return dictionary
    


#%%
def clean_text(file):
    """
    This function iterates over content in a transcript file. 
        It filters out headers, speaker stamps and timestamps.
        In addition to this, special characters and stop words are removed.
    This output is fit for a wordcloud as well as part-of-speech tagging.
    
    Parameters
    ----------
    file : File path to the transcript text file given in function update_dataframe().

    Returns
    -------
    clean_speech (str): Cleaned speech text as a single string with special characters and stop words removed.  

    """
    
    trump_names = ['Donald Trump','Trump','President Trump','President Donald Trump','Donald J. Trump','President Donald J. Trump','Donald J Trump','Donald Trump, Jr.']   # Define Trump names to filter out  
    header_tags = ['Title','Date','Total Speaking Time']   # Define header names to filter out 
    special_chars = ["?",".",",",'“','”','…','"']   # Define special characters
    
    my_stop_words = ["he's","n't","'s","'d","'m","'ve","'re","'ll","’"]   # Definition of additional stop words
    stop_words = nltk.corpus.stopwords.words('english')   # Initialize NLTK stop words
    stop_words.extend(my_stop_words)   # Extend additional stopwords to NLTK stopwords
    
    with open(file,'r',encoding='utf-8',errors='ignore') as f:   # Open file in reading mode
        file_content = f.read()   # Read file
        lines = file_content.splitlines()   # Split file's content into lines
        filtered_lines = []   # Initialize empty list to store filtered lines
        
        for line in lines:   # Iterate over lines
            line = line.strip()   # Remove whitespace on line
            for char in special_chars:   # Iterate over characters in special characters
                line = line.replace(char,"")   # If character is a special characters; remove it
            if '’' in line:  
                line.replace('’',"'")   # If that funky apostrophe is in the text, replace it with a normal one 
            if ':' in line:   # If ':' in line, e.g. line is a timestamp (or a speaker stamp)
                continue   # Skip it
            if any(line.startswith(tag) for tag in header_tags):   # If any line starts with any tag in headers
                continue   # Skip it
            for name in trump_names:   # Loop over Trump names   
                line = re.sub(rf"\b{name}\b(?:\s|,)*(?:jr\.)?",'',line,flags=re.IGNORECASE) # Replace line with ''. Ignore case of letters.

                
                filtered_lines.append(line)   # Append lines to list
                
        filtered_speech = ' '.join(filtered_lines)   # Join the lines in the list into a string with a space
        filtered_speech = filtered_speech.lower()   # Convert to lowercase

        words = word_tokenize(filtered_speech)   # Tokenize the filtered content
        filtered_words = [word for word in words if word not in stop_words]   # Remove stop words
        clean_speech = ' '.join(filtered_words)   # Join the excess words by a space
            
    return clean_speech  


           
                

#%%
def transcript_text(file):
    """
    This function iterates over content in a transcript file. It filters out speaker stamps, timestamps and headers.
    To be returned is the paragraphs divided by lines, e.g. a 'nice' transcript.
    The output is fit for the bar showing the transcript of the speech. 
    
    Parameters
    ----------
    file : File path to the speech text file given in function update_dataframe().
    
    Returns
    -------
    transcript_lines : String with paragraphs from speech divided by line, looking nice and allll of that good stuff

    """
    
    header_tags = ['Title','Date','Total Speaking Time']   # Define header names to filter out
    
    trump_names = ['Donald Trump','Trump','President Trump','President Donald Trump','Donald J. Trump','President Donald J. Trump','Donald J Trump','Donald Trump, Jr.']   # Define Trump names to filter out
    
    with open(file,'r',encoding='utf-8',errors='ignore') as f:   # Open file in reading mode
        file_content = f.read()   # Read file
        lines = file_content.splitlines()   # Split file's content into lines
        transcript_lines = []   # Initialize empty list to store filtered lines
        
        for line in lines:   # Iterate over lines
            line = line.strip()   # Remove whitespace on line
            if ':' in line:   # If ':' in line, e.g. line is a timestamp OR 'Speaker:'
                continue   # Skip it
            if any(line.startswith(tag) for tag in header_tags):   # If any line starts with any tag in headers
                continue   # Skip it
            if any(line.startswith(name) for name in trump_names):   # If any line starts with a Trump name
                continue   # Skip it
            else:
                transcript_lines.append(line)   # Else append lines to list
        
        transcript_lines = [line for line in transcript_lines if line]   # Remove empty lines
        
        transcript = '\n\n'.join(transcript_lines)   # Join the lines in the list with new lines in between 
            
    return transcript
            

#%%
"""
Using the function update_dataframe() an updated csv file with the further information is be created.

Updated dataframe is written to a .csv file.

"""
import pandas as pd
import os
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('tagsets')
nltk.download('tagsets_json')
from nltk.corpus import stopwords

# Assign directory and file to variables
speeches_directory='C:/Users/mette/OneDrive/Documents/1_semester/programmering/eksamen/speeches_w_titlenames1'
csv_file='C:/Users/mette/OneDrive/Documents/1_semester/programmering/eksamen/speeches_w_titlenames1/trump_data.csv'

# Use function and assign to variable
updated_trump_data=update_dataframe(csv_file,speeches_directory)

# Write updated DataFrame to file with no row names (index=False)
updated_trump_data.to_csv('updated_trump_data.csv',index=False,encoding='utf-8-sig')