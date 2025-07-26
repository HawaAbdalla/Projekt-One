# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 06:45:22 2024

@author: PC
"""

#%%
"""
This program will create a list with the date;link pairs from the .txt file

"""

# Assign file containing links and dates to a variable
file='links_trump.txt'

links_trump=[]   # Initialize empty list 

with open(file,'r',encoding='utf-8') as f:   # Open file in reading mode
    lines = f.readlines()   # Read lines of file

lines = [line.strip() for line in lines if line.strip()]   # Assign lines to a variable, discarding empty lines

# Iterate over range of lines with start = 0, end = 2
for i in range(0,len(lines),2):
    date = lines[i]   # Assign item at index position i to a variable: this is the date
    link = lines[i+1]   # Assign item at index position i + 1 to a variable: this is the link
    links_trump.append((date,link))   # Append date;link pair to list

#%%
import re
import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
from datetime import timedelta

# Initialize a .csv file to store data
csvfile = 'trump_data.csv'

with open(csvfile,'w',newline="",encoding='utf-8') as file:   # Open .csv file in writing mode
    fieldnames = ['Title', 'Date', 'Length']   # Set column names
    writer = csv.DictWriter(file,fieldnames=fieldnames)   # Initialize .csv writer
    writer.writeheader()   
    
    for j,(date,link) in enumerate(links_trump,start=1):   # Iterate over date;link pairs in list of dates and links. Index 'j' provides the position of items. Start is set to 1: this is the link
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}   # Initialize header
        try:
            request = requests.get(link,headers=headers,timeout=10)   # Send request to webpage
            if request.status_code != 200:   # A 200 response is ‘OK’ showing that the request has been successful. Response messages can also be viewed by creating an object and print(object.status_code). /oxylabs.io 
                print(f'Request failed: {link}\n Status code: {request.status_code}\n\n')   # Print error message if request failed and state error code
                continue   # Continue is request is succesful
            
            soup = BeautifulSoup(request.text,'html.parser')   # Parse content from webpage
            title = soup.find('title')   # Get the title
            title_text = title.get_text()   # Get text from title and assign to variable
            sanitized_title = sanitize_filename(title_text)   # Use function 'sanitized_filename' on title text
            
            trump_lines,timestamps = speaker_colon_format(soup,title,date)   # Attempt to use first speaker stamp format to get content
            
            if len(trump_lines)<5:   # If total length of content with the above speaker stamp format is below 5,
                print(f'Error in finding lines with "Speaker: (timestamp)" format for {link}\n Trying other format...\n\n')   # Print an error message stating the link
                trump_lines,timestamps = timestamp_colon_format(soup,title,date)   # Try second speaker stamp format to get content
                
                if not trump_lines:   # If both formats fail, 
                    print(f'Both formats failed for {link} number {j}\n Please inspect URL manually\n\n')   # Print error message
                    continue   # Continue executing program           
         
            minutes,seconds = speaking_time(timestamps)   # Use function speaking_time() to calculate total speaking time

            writer.writerow({'Title': sanitized_title, 'Date': date,'Length': f'{minutes}:{seconds}'})   # Write information about title, date and speaking time to .csv file

            file = f'{sanitized_title}.txt'   # Initialize file to store the content of transcripts with the title as file names
            write_files(file,title,date,trump_lines,minutes,seconds)   # Use function write_files() to write content to files
        
        except Exception as e:   # Set except and print error message for whatever might be
            print(f'Error: {link} - {e}')
            
        time.sleep(3)

#%%
"""
Function replaces ':' and '/' with accepted special characters for file names.
This is applied to the title text and ensures files with transcript content can be saved named by their titles.

"""

def sanitize_filename(title):
    sanitized_title = title.replace('/', '.').replace(':', '.')   # Replace '/' and ':' with '.'

    sanitized_title = re.sub(r'[\\*?"<>|]', '_', sanitized_title)   # Replace any other special characters with '_'
    
    return sanitized_title   # Return the title text

#%%
"""
Function considers content that contains speaker patterns in the format of: 'Speaker ():'. 
The content is split by the pattern. The content is then iterated over and appended to a list storing the transcript and to a list storing timestamps. 
The function returns the appropriate lists.

"""

def timestamp_colon_format(soup,title,date):
    content = soup.find('div', {'id': 'main-content'})   # Find 'div' tags by ID and assign to variable 
    content = content.get_text()   # Get content as text
    
    # Pattern for recognizing speaker stamp format: 'Speaker ():
    pattern = r'([A-Za-z ,.\'-]+(?: [A-Za-z0-9]+)?)\s*\((\d{1,2}:\d{2}(?::\d{2})?)\)\s*:|(\(\d{1,2}:\d{2}(?::\d{2})?\))'
    
    lines = re.split(pattern,content)   # Split the content by the pattern
    filtered_lines = [line for line in lines if line and line.strip()]   # Remove 'None' values, whitespace, etc. and assign to variable 
    
    # List of various ways Trump is referred to in transcripts
    trump_names = ['Donald Trump','Trump','President Trump','President Donald Trump','Donald J. Trump','President Donald J. Trump','Donald J Trump']   
    
    trump_lines = []   # Initialize empty list to store the lines connected to Trump
    timestamps = []   # Initialize empty list to store timestamps
    
    obtaining=False   # Initialize a variable to control appending of lines. Set to False
    
    for line in filtered_lines:   # Loop over lines of content
        if ':' in line and len(line)<10 and line not in timestamps:   # If line has a colon and less than 10 characters, it's most likely a timestamp. We ensure that it is not already stored in list containing timestamps as well.
            timestamps.append(line)   # Add timestamp to list
        if any(line.startswith(name) for name in trump_names):   # If any line starts with any name in list of Trump names
            obtaining=True   # Start obtaining and append to list
            trump_lines.append(line)
        elif re.match(r'[A-Za-z ,.\'-]+',line) and not any(line.startswith(name) for name in trump_names):   # If line has a general speaker pattern, and doesn't start with any name in 'trump_names'
            obtaining=False   # Stop obtaining
        elif line.strip().startswith('Speaker') or line.strip().startswith('Crowd') or line.strip().startswith('Audience'):   # If line starts with 'Speaker', 'Crowd' or 'Audience'. Just to be safe:) 
            obtaining=False   # Stop obtaining
        elif obtaining:   # Or else, just obtain lines and append to list
            trump_lines.append(line)
    
    return trump_lines,timestamps   # Return the lists with lines and timestamps


#%%
"""
Function considers content that contains speaker patterns in the format of: 'Speaker: ()'. 
The content is split by the pattern. The content is then iterated over and appended to a list storing the transcript and to a list storing timestamps. 
The function returns the appropriate lists.

"""

def speaker_colon_format(soup,title,date):
    content = soup.find('div', {'id': 'main-content'})   # Find 'div' tags by ID and assign to variable  
    content = content.get_text()   # Get content as text

    # Pattern for speaker stamp format: 'Speaker: ()' 
    #pattern = r'(\b[A-Za-z]+(?: [A-Za-z]+)?\s*:|\(\d{1,2}:\d{2}(?::\d{2})?\))|(\(\d{1,2}:\d{2}(?::\d{2})?\))'
    pattern = r'(\b[A-Za-z]+(?: [A-Za-z]+)?\s*:|\(\d{1,2}:\d{2}(?::\d{2})?\))'

    lines = re.split(pattern,content)   # Split content by pattern
    filtered_lines = [line for line in lines if line and line.strip()]   # Remove 'None' values, whitespace, etc. and assign to variable

    timestamps = []   # Initialize empty list to store relevant lines
    trump_lines = []   # Initialize empty list to store timestamps

    # List of various ways Trump is referred to
    trump_names=['Donald Trump','Trump','President Trump','President Donald Trump','Donald J. Trump','President Donald J. Trump','Donald J Trump']   

    for i,line in enumerate(filtered_lines):   # Loop over index position and line in list of content
        if any(line.startswith(name) for name in trump_names):   # If line[i] starts with any name in trump_names
            trump_lines.append(line)   # Add line[i] to list
            if i+1<len(filtered_lines):   # i+1 is the timestamp. If i+1 is within bounds of the content,
                timestamps.append(filtered_lines[i+1])   # Add that line to timestamps list
                trump_lines.append(filtered_lines[i+1])   # As well as list of lines
            if i+2<len(filtered_lines):   # i+2 is the paragraph. If i+2 is within bounds of the content,
                trump_lines.append(filtered_lines[i+2])   # Add that line to list of lines
        
    return trump_lines,timestamps   # Return the lists with lines and timestamps  
     
#%%
"""
Function writes title, date, speaking time and transcript lines to files.

"""

def write_files(file,title,date,trump_lines,minutes,seconds):
    with open(file,'w',encoding='utf-8') as f:   # Open file in writing mode
        f.write(f'Title: {title.get_text()}\n\n')   # Write title to file
        f.write(f'Date: {date}\n\n\n')   # Write date to file
        f.write(f'Total Speaking Time: {minutes} Minutes and {seconds} Seconds\n\n\n')   # Write speaking time to file
        for line in trump_lines:   # Iterate over lines in list containing transcript lines
            line=line.encode('latin-1').decode('utf-8')   # Encode and decode the content
            f.write(f'\n{line}\n')   # Write line to file


#%%
"""
Functions takes a list of timestamps as the parameter. 
Module 'datetime' is used to handle the values and calculate the total speaking time. 

Program iterates over items in a list of timestamps. It handles two timestamps at a time: i-1 and i. 
The difference between these is calculated, and added to a list. 
The difference of the next pair of timestamps is calculated, added to a list, and so forth. 

The program then considers the calculated differences as seconds, and arithmetic operations are used to obtain full minutes and remaining seconds.


"""

def speaking_time(timestamps):
    total_time = timedelta()   # Initialize zero timedelta
    
    # Loop over timestamps starting from second one and one back to calculate each difference
    for i in range(1,len(timestamps)):
        first_ts = timestamps[i-1].strip('()')   # Initialzie a variable to store the timestamp at position i-1. Strip the parenthesis
        second_ts = timestamps[i].strip('()')   # Initialize a variable to store the timestamp at position i. Strip the parenthesis
        
        # Split timestamps into parts by colon
        first_ts_parts = first_ts.split(':')
        second_ts_parts = second_ts.split(':')
        
        if len(first_ts_parts) == 2:   # If total of parts of first timestamp == 2, handle mm:ss format
            first_hour, first_minute, first_second = 0, int(first_ts_parts[0]), int(first_ts_parts[1])   # Hour is 0, and minutes are the first part and seconds the second part. Convert values to integers
        elif len(first_ts_parts) == 3:   # If total of parts of first timestamp == 3, handle hh:mm:ss formart
            first_hour, first_minute, first_second = int(first_ts_parts[0]), int(first_ts_parts[1]), int(first_ts_parts[2])   # Convert values to integers
            
        if len(second_ts_parts) == 2:   # If total of parts of second timestamp == 2, handle mm:ss format and so forth as above 
            second_hour, second_minute, second_second = 0, int(second_ts_parts[0]), int(second_ts_parts[1])
        elif len(second_ts_parts) == 3:
            second_hour, second_minute, second_second = int(second_ts_parts[0]), int(second_ts_parts[1]), int(second_ts_parts[2])
        
        # Create timedelta objects for first and second timestamp
        # A timedelta object represents a duration, the difference between two datetime or date instances. / class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
        first_timedelta = timedelta(hours=first_hour, minutes=first_minute, seconds=first_second)
        second_timedelta = timedelta(hours=second_hour, minutes=second_minute, seconds=second_second)       
        
        time_difference = second_timedelta-first_timedelta   # Calculate difference between first and second timestamp and assign to variable
        total_time += time_difference   # Add difference to total_time
    
    # The total_seconds() function is used to return the total number of seconds covered for the specified duration of time instance.
    total_time_seconds = total_time.total_seconds()   # Use method on the total time 
    minutes = total_time_seconds//60   # Floor division to get full minutes
    seconds = total_time_seconds%60   # Module to get remaining seconds

    return int(minutes),int(seconds)   # Return the calculated minutes and seconds from the total of the calculated time differences

 