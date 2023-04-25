from flask import Flask, request, Response, jsonify, send_file
from flask_cors import CORS
from api import app
import base64
import json
from datetime import datetime
import api.combining as combine
import api.visualize as visualize
import api.defaults as defaults
import api.training as training
import os
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL

song_arr = defaults.SONG_LIST
curr_dir = os.getcwd()
api_dir = os.path.join(curr_dir, 'api')
checkpoint_dir = os.path.join(api_dir, 'checkpoints')
combos_dir = os.path.join(api_dir, 'combos')
data_dir = os.path.join(api_dir, 'data')

#default route
@app.route('/')
def default():
    return "<h1>Hello World!</h1>" \
           "\nThis is my introduction to Flask!" \
           "\nI can write a lot of things on this page.\nLet's get started!"

@app.route('/api/ping', methods=['GET'])
def ping():
    record = request.get_data()
    json_data = json.loads(record)[0]
    return jsonify(pong=str(json_data))

@app.route('/api/test', methods=['GET'])
def test():
    args = request.args
    json_data = {}
    
    if args['song_name']:
        song_name = args['song_name']

    results = search_song(song_name)
    json_data = cursor_to_json(download_song(results[0], results[1]))
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#get all current songs
@app.route("/api/songs", methods=["GET"])
def get_song_list():
    json_data = {}

    json_data = cursor_to_json(song_arr)
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#does all the steps
@app.route("/api/full", methods=["GET"])
def generate_full_audio():
    args = request.args
    json_data = {}
    
    if args['song_name']:
        song_name = args['song_name']

    if song_name:
        results = search_song(song_name)
        wav_name = download_song(results[0], results[1])
        checkpoint_name = training.demix_with_checkpoint(wav_name)
        training.cleanup(wav_name, checkpoint_name)
        combo_name = combine.combine_with_combo(wav_name, checkpoint_name)
        json_data = cursor_to_json(visualize.generate_embeded_audio(wav_name))
    else:
        json_data = cursor_to_json("""No data provided!""")
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#does all the steps
@app.route("/api/combos", methods=["GET"])
def get_combos():
    json_data = {}

    json_data = cursor_to_json(os.listdir(combos_dir))
    
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#send off a song and get the visualization data for it
@app.route("/api/visualize", methods=["GET"])
def get_visualization():
    args = request.args
    json_data = {}
    
    if args['combo_name']:
        combo_name = args['combo_name']
        
    if combo_name:
        return send_file(visualize.visualize(combo_name), mimetype='image/png')
    else:
        json_data = cursor_to_json("""No data provided!""")
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#send off a song and get the visualization data for it
@app.route("/api/audio", methods=["GET"])
def get_audio():
    args = request.args
    json_data = {}
    
    if args['combo_name']:
        combo_name = args['combo_name']
        
    if combo_name:
        json_data = cursor_to_json(visualize.generate_audio(combo_name))
    else:
        json_data = cursor_to_json("""No data provided!""")
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#send off a song and get the visualization data for it
@app.route("/api/embeded_audio", methods=["GET"])
def get_embeded_audio():
    args = request.args
    json_data = {}
    
    if args['combo_name']:
        combo_name = args['combo_name']
        
    if combo_name:
        json_data = cursor_to_json(visualize.generate_embeded_audio(combo_name))
    else:
        json_data = cursor_to_json("""No data provided!""")
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# takes a song name and will try to demix it
@app.route("/api/demix", methods=["GET"])
def do_demix():
    args = request.args
    json_data = {}
    
    if args['song_name']:
        song_name = args['song_name']

    json_data = {}

    json_data = cursor_to_json(training.demix(song_name))
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#combine a checkpoint into a proper audio source and output it to the combos folder
@app.route("/api/create_audio", methods=["GET"])
def get_songs():
    args = request.args
    json_data = {}
    
    if args['song_name']:
        song_name = args['song_name']
    
    if args['checkpoint_name']:
        checkpoint_name = args['checkpoint_name']

    if song_name and checkpoint_name:
        json_data = cursor_to_json(combine.combine(song_name, checkpoint_name))
    else:
        json_data = cursor_to_json("""No data provided!""")
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#Extras-----------------------------------------------------------------------------

def download_song(id, title):
    ydl_opts = {
        'format': 'wav/bestaudio/best',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'paths': {
            'home': "api/data",
        },
        'outtmpl': {
            'default': title,
        },
    }
    urls = ["https://www.youtube.com/watch?v=%s" %(id)]
    

    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(urls)

    filename ='%s.wav' %(title)
    return filename

def search_song(song_name):
    yt = YTMusic()
    query = song_name
    topResult = yt.search(query)[0]
    videoId = topResult["videoId"]
    videoTitle = topResult['title']
    videoArtist = topResult['artists'][0]['name']
    return videoId, videoTitle, videoArtist

def bytes_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode('utf-8')

def cursor_to_json(cursor):
    json_data = json.dumps(cursor, indent=4)
    return json_data