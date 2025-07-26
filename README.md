# Projekt-One
Analyze Donald Trump's Speeches 


web_scraping.py
My program executes browser automation using the Selenium package. The program scrolls on the page and loads more until a certain condition is met. When the condition is met, the program scrolls to the top of the page while appending links and dates that are related to Trump speeches. The links and dates are then written to a .txt file.
I faced obstacles during this process. The initial website that I had to scrape had an unstable scrolling mechanism. I were not able to gather a consistent number of links. This left us working with a different website, which also caused issues since the layout changed sporadically throughout my work. 

processing_url_content.py
My script can be divided into two major parts: getting content from URLs and processing the content appropriately into a dataframe.
In the first part, I have iterated over each of the gathered links and sent requests to the websites. The content is then retrieved, split into fitting formats and iterated over, in order to only gather the relevant information related to Trump. This has included gathering speaker stamps, time stamps and paragraphs associated with him. The title, date and total speaking time of each transcript is written as data to a .csv file. Full transcripts are written to individual .txt files. 

updating_dataframe.py 
In the second part, i have extended the .csv file with further information in order to continue building my app. Several columns are added to the .csv file after reading it into a pandas dataframe. These include a column containing cleaned transcript, full transcript, and POS-tagging of the transcript. This is done by iterating over a directory containing the .txt files with transcript and matching them by their file name and the connected row data in the ‘Title’ column. Several functions are deployed in order to process the content to fit the output  I wished to obtain. Finally, this dataframe is written to an updated .csv file. 

dash_app.py / generating_general_wordcloud.py 
For the final part, I have developed a graphical user interface containing a timeline displaying lengths of each speech, a search bar to highlight speeches with a given keyword, a dynamically updated word cloud determined by a speech and POS-tagging, as well as a display of the transcript. 
A deviation that has been made in this part is related to the search for keywords and highlighting of bars. my program removes the bars of the speeches that do not contain the keyword rather than highlighting the ones that do
