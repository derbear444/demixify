from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from api import app
import base64
import json
from datetime import datetime
import api.combining as combine
import api.visualize as visualize
import api.defaults as defaults

song_arr = defaults.SONG_LIST

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

#get all current songs
@app.route("/api/songs", methods=["GET"])
def get_song_list():
    json_data = {}

    json_data = cursor_to_json(song_arr)
        
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
        json_data = cursor_to_json(visualize.visualize(combo_name))
    else:
        json_data = cursor_to_json("""No data provided!""")
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#combine a checkpoint into a proper audio source and output it to the combos folder
@app.route("/api/create_audio", methods=["POST"])
def get_songs(song_name, checkpoint_name):
    json_data = {}
    
    if song_name and checkpoint_name:
        json_data = cursor_to_json(combine.combine(song_name, checkpoint_name))
    else:
        json_data = cursor_to_json("""No data provided!""")
        
    resp = Response(json_data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

#Extras-----------------------------------------------------------------------------

def bytes_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode('utf-8')

def cursor_to_json(cursor):
    json_data = json.dumps(cursor, indent=4)
    return json_data