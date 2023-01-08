from pymongo import MongoClient
from http.server import BaseHTTPRequestHandler
import os
from bson.objectid import ObjectId
import json
import ast


class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """
        A post method that handles a request wih the parameter "input" and writes the value of input
        """
        # Get the data in the request
        content_length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(content_length)
        content = ast.literal_eval(body.decode('utf-8'))
        docbase = content['document-base']
        
        # Create ID
        id = ObjectId()

        # Connect to MongoDB and create the conversation log
        MONGODB_URL = os.getenv("MONGODB_URL")
        db = MongoClient(MONGODB_URL)['chatassist-development']
        db.ConversationLog.update_one({"_id": id}, {"$set": {"document-base": docbase, "conversation": []}}, upsert=True)
        
        # Return the ID
        res = str(id)
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        d = {'message': res}
        res_body = json.dumps(d)
        self.wfile.write(res_body.encode())
