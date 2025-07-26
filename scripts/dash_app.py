# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 15:27:57 2024

@author: PC
"""

#%%
import dash
from dash.dependencies import Input, Output
from dash import dcc, html
import plotly.express as px
import pandas as pd
import plotly.express as px 
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import plotly.graph_objects as go
import base64
from io import BytesIO


# Read .csv file into a pandas dataframe
trump_data = pd.read_csv('updated_trump_data.csv',encoding='utf-8-sig')

# Generate bar plot
data = go.Bar(
    x = trump_data['Title'],   # Row data from 'Title' column on x-axis
    y = trump_data['Minutes'],   # Row data from 'Minutes' column on y-axis
    marker = dict(color='#e81b23')   # Set color for bars
    )
layout = go.Layout(xaxis_title = None,   # Set title to None for both x-axis and y-axis
    yaxis_title = None,   
    xaxis = dict(showticklabels = False),   # Hide ticklabels on both x-axis and y-axis
    yaxis = dict(showticklabels = False),
    margin = dict(l=0, r=0, t=0, b=0),   # Set margin 
    plot_bgcolor = '#fde8e8')   # Set background color

fig = go.Figure(data = data, layout = layout)   # Make bar plot


# Assign file path to image of the general wordcloud
image_path = 'C:/Users/PC/OneDrive/Documents/1_semester/programmering/eksamen/assignment_2/dash/general_wordcloud.png'
def b64_image(image_file):   # Function to generate the 'starter' wordcloud
    with open(image_file,'rb') as f:
        image = f.read()
    return 'data:image/png;base64,'+base64.b64encode(image).decode('utf-8')   # Encode and decode image file fit for a browser to read
# Assign the general wordcloud to a variable
general_wordcloud = b64_image(image_path)   # Assign the general wordcloud to a variabel



app = dash.Dash(__name__)
                
app.layout = html.Div([
    # Title section
    html.H1('Donald Trump Speeches', style={
        'textAlign': 'center',
        'font-family': 'Verdana',
        'color': '#E81B23'
    }),
    
    # Main content section / outer wrapper
    html.Div([
        
    # Left section of app: bar plot, text area and search bar.
        html.Div([
            dcc.Input(   # Search bar
                id = "search-bar",
                type = 'text',
                placeholder = 'Search for Keywords here...',
                style = {'width':'50%','padding':'10px','margin':'10px auto','display':'block'}
                ),
            dcc.Graph(   # Bar plot
                figure = fig,
                id = 'speeches-timeline',
                style = {'height': '100%','width': '100%'}
                ),
            html.Div([   
            dcc.Textarea(   # Text area 
                id = 'text-transcript',
                value = 'Click Bar for Transcript...',
                style = {'width': '100%','height': '180px'}
            )
        ], style = {
            'margin-top':'10px',   
            'width':'100%',
            }),
    ], style = {   # Styling of the whole container / outer wrapper on the left
        'width':'46%',
        'display':'inline-block',
        'vertical-align':'top',
        'margin':'1%',
        'height':'500px'
    }),      
              
              
              
    # Right section of app: wordcloud and POS checkboxes section
    html.Div([
        html.Div(
            id = 'wordcloud-output',
            style = {'height':'100%','width':'100%'}   # Styling of wordcloud container
        ),
        html.Div([
            html.Div([
                dcc.Checklist(   # Checkboxes for POS tagging
                    id = 'pos-checkbox',
                    options = [{'label': tag, 'value': tag} for tag in [
                        'CC','CD','DT','IN','JJ','JJR','JJS','MD',
                        'NN','NNP','NNPS','NNS','PDT','PRP','RBR',
                        'RBS','RP','UH','VB','VBD','VBG','VNB','VBZ'
                        ]],
                    inline = True,
                    labelStyle = {'margin-right':'28px','margin-bottom':'12px'}
                    )
                ]),  
            ],style = {   # Styling of checkboxes container
                'width':'70%',
                'margin-top':'100px',
                'margin':'10px auto',
                'border-style':'solid',
                'border-color':'red',
                'padding':'15px'
                })
        ], style = {   # Styling of the whole container / outer wrapper on the right
            'width':'46%',
            'display':'inline-block',
            'vertical-align':'top',
            'margin':'4%',
            'height':'500px'
            })
        ], style = {
            'display':'flex',
            'justify-content':'space-between'          
    })
])



def part_of_speech(text,selected_categories):
    words = word_tokenize(text)   # Tokenize text
    result = nltk.pos_tag(words)   # Tag words
    
    tagged_words = [word for word,tag in result if tag in selected_categories]   # Define the tagged words in relation to the available checkboxes
    no_duplicates = list(set(tagged_words))   # Convert the above list to a set to remove duplicates
    tagged_text = ' '.join(no_duplicates)   # Join the content to a string in order to make wordcloud
    
    return tagged_text



            
def generate_wordcloud(clean_text):   # Function takes item in 'Clean_Text' column
    wordcloud = WordCloud(background_color = 'white',   # Generate wordcloud
                          max_words = 75,
                          color_func = lambda *args,**kwargs:(232,27,35),
                          width = 800, 
                          height = 500).generate(clean_text)
    
    # Just like what we do with variables, data can be kept as bytes in an in-memory buffer when we use the io module’s Byte IO operations. / digitalocean.com
    img = BytesIO()   
    
    # to_image() converts wordcloud into a 'Pillow Image Object'. (See: Python Imaging Library)
    # .save() saves an image to a file or a file-like object. In this case, the 'BytesIO' object from above
    wordcloud.to_image().save(img,format='PNG')   
    
    # Moves 'file pointer' back to the beginning of the file from the file. Else, it stays at the end of the written data.
    img.seek(0)   
    
    # Encode the bytes in PNG image saved in the 'BytesIO' object into a 'Base64' string and decode it into a 'utf-8' text format.
    # .getvalue() retrieves all the binary data stored in the 'BytesIO' object 'img': At this point, the data is in binary format (e.g., b'\x89PNG...).
    # 'img_base64' now contains the 'Base64'-encoded representation of the PNG image as a plain text string. 
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')   
    
    # The 'Base64' string is used to create a 'data URL' which is a method for embedding image data directly into web pages without requiering a separate file.
    # The line embeds it in a 'URI scheme' data which browser interpret as an inline image. 
    return f"data:image/png;base64,{img_base64}"
   

    

# Callback that updates wordcloud when a clicked bar or a ticked checkbox is detected      
@app.callback(
    Output('wordcloud-output','children'),
    [Input('speeches-timeline','clickData'),
     Input('pos-checkbox','value')],
    )
def display_wordcloud(clickData,selected_categories):   
    if clickData == None:   # If no click is detected,
        return html.Img(src = general_wordcloud, style = {'height': '100%', 'width': '100%'})   # Show the general wordcloud defined earlier
    title = clickData['points'][0]['x']   # Detect the bar clicked by referring to the title on the x-axis
    text = trump_data[trump_data['Title']==title]['Clean_Text'].values[0]   # Get the transcript relating to the title
    
    if not selected_categories:   # If no checkboxes are selected
        wordcloud_img = generate_wordcloud(text)   # Generate word cloud for the overall speech
        return html.Img(src = wordcloud_img, style = {'height':'auto','width':'100%'})
    
    tagged_text = part_of_speech(text, selected_categories)   # Use function to tag the transcript and pull out the selected checkboxes
    wordcloud_img = generate_wordcloud(tagged_text)   # Generate wordcloud according to the checkboxes selected
    
    return html.Img(src = wordcloud_img, style = {'height': 'auto', 'width': '100%'})   # Return POS wordcloud




# Callback that updates text box with transcript when a bar is clicked
@app.callback(
    Output('text-transcript','value'),
    [Input('speeches-timeline','clickData')]
    )
def display_transcript(clickData):
    if clickData == None:   # If clickData is None, return output below
        return 'Click Bar for Transcript...'
    title = clickData['points'][0]['x']   # Detect the bar clicked by referring to the title on the x-axis
    transcript = trump_data[trump_data['Title']==title]['Transcript_Text'].values[0]   # Generate transcript according to the checkboxes selected
    
    return transcript



# Callback updates bar plot when user types a word in the search bar
@app.callback(
    Output('speeches-timeline', 'figure'), 
    [Input('search-bar', 'value')]          
)
def update_bars(user_input):
    if user_input:
        filtered_data = trump_data[trump_data['Transcript_Text'].str.contains(user_input,case=False,na=False)]   # If 'user_input' is not empty, look for input in data in the column 'Transcript_Text'
    else:
        filtered_data = trump_data   # If 'user_input' is empty, just leave the data as is.

    if filtered_data.empty:   
        x_data = ['No Results']   # If 'filtered_data' is empty, with None values, whatever; just assign some absence of results
        y_data = [0]
    else:
        x_data = filtered_data['Title']   # If 'filtered_data' is not empty, assign 'Title' as x-axis value, and 'Minutes' as y-axis value.
        y_data = filtered_data['Minutes']

    data = go.Bar(   # Update the bar with the x-axis and y-axis determined by the user input from above.
        x = x_data,
        y = y_data,
        marker = dict(color='#e81b23')
    )

    layout = go.Layout(
        xaxis_title = None,
        yaxis_title = None,
        xaxis = dict(showticklabels=False),
        yaxis = dict(showticklabels=False),
        margin = dict(l=0, r=0, t=0, b=0),
        plot_bgcolor = '#fde8e8'
    )

    updated_bars = go.Figure(data = data, layout = layout)
    return updated_bars



if __name__ == '__main__':
    app.run_server(debug = True, port = 8080)