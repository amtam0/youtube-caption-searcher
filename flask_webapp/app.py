# -*- coding: utf-8 -*-
import flask

import pandas as pd
import webvtt
from wordcloud import WordCloud
import matplotlib.pyplot as plt

import datetime
import os
import base64
from io import BytesIO

import youtube_dl

pd.set_option('display.max_colwidth', -1)

app = flask.Flask(__name__)
@app.route('/', methods=['GET', 'POST'])

def login():
    result=wordcloud_img=video_link=link=captions=error=""

    if flask.request.method == 'POST':
        if flask.request.form['link'] == '' or flask.request.form['keyword'] == '':
            error = 'Invalid Credentials. Please try again.'
        else:
            link = flask.request.form['link'].split('&')[0]
            keyword = str(flask.request.form['keyword'])
            language = str(flask.request.form['Language'])
            print("language",language)
            result,video_link,wordcloud_img = find_keyword(link=link,keyword=keyword,language=language)

    return flask.render_template('app.html',tables=result,videos=video_link,image=wordcloud_img,error=error)

def make_clickable(url_link=None):
    return '<a href="{}"  target="_blank">{}</a>'.format(url_link,"At sec {}".format(url_link.split("?start=")[-1]))

def find_keyword(link=None,keyword=None,language=None,tmp=""):

    """
    find all timestamp where keyword appears in YOUTUBE VIDEO
    CAPTION MUST BE ACTIVE
    """
    
    #TODO CATCH VIDEOS WITH NO CAPTIONS

    W,H = 640,360
    keyword = keyword.lower()
    link = link.replace('watch?v=','embed/')
    video_link =  """<iframe width="{}" height="{}" src={} frameborder="0" allowfullscreen></iframe>""".format(W,H,link)

    # subtitles =  os.system("youtube-dl --write-auto-sub --sub-lang {} --skip-download {}".format(language,link))
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'subtitleslangs': [language],
    'outtmpl': '{}example.%(ext)s'.format(tmp),
    'skip_download':True,
    'writeautomaticsub':True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    try:
        captions = webvtt.read("{}example.{}.vtt".format(tmp,language))
    except FileNotFoundError:
        return "no cc found","",""
    df = pd.DataFrame()
    df['text'] = [caption.text.replace("\n"," ").strip().lower() for caption in captions]
    df['start_str'] = [caption.start for caption in captions]
    df['stop_str'] = [caption.end for caption in captions]
    
    df['start'] = df['start_str'].apply(lambda x:datetime.datetime.strptime(x,'%H:%M:%S.%f'))
    df['stop'] = df['stop_str'].apply(lambda x:datetime.datetime.strptime(x,'%H:%M:%S.%f'))

    df['start1'] = df['start'].apply(lambda x:x.second+float("0.{}".format(x.microsecond)))
    df['stop1'] = df['stop'].apply(lambda x:x.second+float("0.{}".format(x.microsecond)))

    df['start_totalseconds'] = df['start'].apply(lambda x:round(x.hour*3600+x.minute*60+x.second+float("0.{}".format(x.microsecond))))
    df['start_link'] = df['start_totalseconds'].apply(lambda x:link+"?start={}".format(x))
    df['delta'] = df['stop1'] - df['start1']
    # Remove files with duration under 0.1 second
    df = df[df["delta"]>0.1]

    result = df[['start_str','start_totalseconds',"start_link"]][df['text'].str.contains(keyword)]
    #remove results that have less than 5 seconds gap
    result['check'] = (result['start_totalseconds'] - result['start_totalseconds'].shift(1)).fillna(999)
    result = result[result["check"] > 5]
    
    # WORDCLOUD*************
    wordcloud_img=""
    text=df['text'].str.cat()
    wc = WordCloud(width=W, height=H)
    wordcloud = wc.generate(text)
    wordcloud.to_file("{}file.png".format(tmp))
    with open("{}file.png".format(tmp), "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    wordcloud_img = "<img src='data:image/png;base64,{}'>".format(encoded)
    # WORDCLOUD*************

    result['start_link'] = result['start_link'].apply(make_clickable)

    result.drop_duplicates(subset=['start_link'],inplace=True)
    # result = result.style.set_properties(**{'text-align': 'center'})
    result = result[["start_link"]]
    if result.empty:
        result.columns = ["Keyword not found"]
    else:
        result.columns = ["Keyword found"]
    result = result.reset_index(drop=True).style.hide_index().set_properties(**{'background-color': 'white', 
                                    'border-color': 'black',
                                    'border-style' :'solid',
                                    'text-align': 'center',
                                    'border-width': '1px',                                               
                                    'color': 'black'})\
                                    .set_table_styles([dict(selector='th', props=[('text-align', 'center')])])\
                                    .render()
    
    #Remove caption file after using it
    os.system("rm {}*.vtt".format(tmp))
    os.system("rm {}*.png".format(tmp))

    return result,video_link,wordcloud_img

if __name__ == '__main__':
    app.run(debug=True)