# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 15:31:34 2024

@author: PC
"""

#%%
import os
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk


"""
Add all transcript text into a single file. 
This content is used for the general over-all wordcloud.

"""
# Set directory with speech text files
speeches_directory = 'C:/Users/mette/OneDrive/Documents/1_semester/programmering/eksamen/speeches_w_titlenames1'

# Loop over files in directory and return a list of file names using os.listdir() if file name is .txt.
# Assign to variable
file_names = [file for file in os.listdir(speeches_directory) if file.endswith('.txt')]

# Empty string to hold content
all_speeches = ''

# List of Trump names and header tags to remove
trump_names = ['Donald Trump','Trump','President Trump','President Donald Trump','Donald J. Trump','President Donald J. Trump','Donald J Trump']   
header_tags = ['Title','Date','Total Speaking Time']

# Loop over each file in directory
for file_name in file_names:
    with open(os.path.join(speeches_directory,file_name),'r',encoding='utf-8') as file:
        file_content = file.read()
        lines = file_content.splitlines()   # Split content into lines
        
        clean_lines = []   # Intialize empty list to store lines
        
        for line in lines:   # Iterate over lines
            if ':' in line:   # If ':' in line 
                continue   # Skip it
            if any(line.startswith(tag) for tag in header_tags):   # Skip the headers in text file
                continue
            for name in trump_names:
                line=re.sub(rf"\b{name}\b",'',line)   # Replace line with empty string if line in 'trump_names'. \b is a word boundary to ensure only exact words are matched.
         
            # Append lines to list and strip whitespace
            clean_lines.append(line.strip())
        
        # Join content from list into a single string
        cleaned_speech = ' '.join(clean_lines)
        
        # Add the cleaned speech to the variable storing everything
        all_speeches += cleaned_speech

# Convert to lowercase and just strip it again for good measure
all_speeches = all_speeches.lower().strip()

with open('all_speeches.txt','w',encoding='utf-8') as f:   # Write the text to a file
    f.write(all_speeches)
    
    

#%%
"""
Replace and remove all special characters in text file with all of the speeches.
    First attempt was writing the characters to an empty string and then writing to file separately (Too slow).
    Writing directly to output file is much faster.

"""

special_chars = ["?",".",",",'“','”','…','"']   # Define special characters

with open('all_speeches.txt','r', encoding='utf-8') as input_file, open('all_speeches_clean.txt','w', encoding='utf-8') as output_file:   # Open input file with all transcrips in reading mode, open output file to store clean text in writing mode
    for line in input_file:   # Loop over lines in input file
        line = line.replace("’", "'")   # Replace that characters with a normal one
        for char in line:   # Iterate over characters in line
            if char not in special_chars:   # If character is not a special character
                output_file.write(char)   # Write it to the output file
    

#%%
"""
Word cloud that plots the textual summary of all speeches.

"""
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt

my_stop_words = ["he's","n't","'s","'d","'m","'ve","'re"]   # Definition of additional stop words
stop_words = nltk.corpus.stopwords.words('english')   # Intialize NLTK stopwords
stop_words.extend(my_stop_words)   # Extend additional stopwords to NLTK stopwords

with open('all_speeches_clean.txt','r',encoding='utf-8') as f:   # Open file with all of the speeches cleaned
    file_content=f.read()
    
words = word_tokenize(file_content)   # Tokenize the content

filtered_words = [word for word in words if word not in stop_words]   # Filter out stop words

filtered_text = ' '.join(filtered_words)   # Join the remaining words with a space

# Generate word cloud
wordcloud = WordCloud(background_color = 'white',
                      colormap = 'hot',
                      width = 800, 
                      height = 400).generate(filtered_text)

# Show wordcloud and save it
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off') 
plt.show()
