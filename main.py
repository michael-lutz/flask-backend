from flask import Flask, request
import json
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

import sys
sys.path.insert(0, '/src/')
from src.ChatAssist import ChatAssist

app = Flask(__name__)

MONGODB_URL = os.getenv("MONGODB_URL")
client = MongoClient(MONGODB_URL)
database = client['chatassist-development']

# accept post requests
@app.route("/hello___", methods=["POST"])
def hello_world():
    content = request.get_json()
    res = content['input']
    d = {'message': res}
    res_body = json.dumps(d)
    return res_body, 200

@app.route('/initialize_convo', methods=['POST'])
def initialize_convo_handler():
    """
    A post method that handles a request wih the parameter "input" and writes the value of input
    """
    # Getting access to database defined above
    global database
    db = database

    content = request.json
    text = content['question']
    domain = content['domain']
    id = str(ObjectId())

    bot = ChatAssist(db=db, id=id, domain=domain, convo_buffer=[])
    res = bot.converse(text)

    d = {'message': res, 'id': id}
    res_body = json.dumps(d)
    # stringify the json
    return res_body, 200

@app.route('/generate_response', methods=['POST'])
def generate_response_handler():
    """
    A post method that handles a request wih the parameter "input" and writes the value of input
    """
    # Getting access to database defined above
    global database
    db = database

    content = request.json
    text = content['question']
    id = content['conversation_id']


    instance = db.ConversationLog.find_one({"_id": ObjectId(id)})
    log, domain = instance['conversation'], instance['domain']
    bot = ChatAssist(db=db, id=id, domain=domain, convo_buffer=log) # In the future, have the bot be created by selection / default and stored somewhere

    # Creating the ChatAssist instance after fetching chat log from database
    

    res = bot.converse(text)

    d = {'message': res, 'id': id}
    res_body = json.dumps(d)
    # stringify the json
    return res_body, 200



if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
