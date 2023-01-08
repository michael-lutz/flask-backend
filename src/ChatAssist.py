from flask import Flask, request, jsonify
from pymongo import MongoClient
import openai
import numpy as np
import os
import ast
from bson.objectid import ObjectId
import json
from enum import Enum

class ControlFlowFlags(Enum):
    # TODO think about other conversational flow considerations we may want to keep in mind
    REFER_PREVIOUS = 0 # Refer to previous line in conversation when searching to construct prompt

class ChatAssist:
    def __init__(self, db, id, domain, convo_buffer=[]) -> None:
        self.db = db
        self.conversation_buffer = convo_buffer
        self.MAX_CHARS = 7500
        self.domain = domain
        self.id = id

        # TODO Cache embeddings for these in a local file somewhere and load the file content instead
        self.ctrl_flow_prompts = {
            ControlFlowFlags.REFER_PREVIOUS: [self._get_emb("Can you elaborate on the previous point?")]
        }

    def converse(self, text):
        """
        Sends input text, retrieves model output.
        """
        # Retrieving Docs
        sorted_docs, flags = self._sort_documents(text)
        
        if flags == ControlFlowFlags.REFER_PREVIOUS and len(self.conversation_buffer) > 0:
            sorted_docs, flags = self._sort_documents(self.conversation_buffer[-1])

        # Construct prompt instructions
        self.conversation_buffer.append(f"[User]: {text}")
        convo = self._compile_convo()
        prompt_end = "You are a chatbot customer support agent for a company and should continue the conversation in a cordial and professional manner using the information provided above alone to guide your responses. If you don't know the answer or the information is not provided above, refer the customer to 800-403-8023. Do not go off-topic or talk about irrelevant things--you are a customer service chatbot\n"

         # Figure out which sections to add based on our character budget
        sections_to_add = []
        remaining_budget = self.MAX_CHARS - len(prompt_end) - len(convo) - len("[Agent]:")
        for section in sorted_docs:
            # Cost is the number of characters that need to be inserted into the prompt in order to provide an answer
            if section[3] < remaining_budget:
                sections_to_add.append(section)
                remaining_budget -= section[3]

            # We can end early if we are within a few characters of the budget
            if remaining_budget < 20:
                break

        # Resort sections that we want to include in the prompy based on section / page ordering
        prompt = ""
        sections_to_add.sort(key=lambda x: x[1] * 10000 + x[2]) # This limits maximum number of pages to 10k
        for section in sections_to_add:    
            prompt += self._format_section(section[0])

        # Put all the pieces together
        final_prompt = prompt  + prompt_end + convo + "[Agent]:"

        # Get response
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=final_prompt,
          temperature=0.6,
          max_tokens=2048,
          top_p=1,
          frequency_penalty=1,
          presence_penalty=1
        )
        response_text = response["choices"][0]["text"]
        self.conversation_buffer.append("[Agent]:" + response_text)

        self._add_log_db()
        return response_text
    
    def _format_section(self, section):
        return section["title"] + ":\n" + section["content"] + "\n\n"

    def _get_emb(self, text):
        response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
        return np.array(response['data'][0]['embedding'])

    def _sort_documents(self, text):
        """
        Performs inner product between input text and all documents in database,
        returns sorted list of documents in descending order of similarity.
        """

        # Get all pages from database 
        # TODO Can we move this to the constructor so we only pull once? Same for unravellign sections. In theory should only need to be done once per conversation.
        pages = []
        filter={'_id': ObjectId('63b627e8c6fe36f54dcf2a7e')} # TODO Update filter based on user configuration
        for page in next(self.db.ScrapedDomains.find(filter=filter))["pages"]:
            pages.append(page)

        # Unravel sections and section meta-data (section object, page index, section index, section length)
        X = []
        sections = []
        for p, page in enumerate(pages):
            for s, section in enumerate(page['sections']):
                sections.append((section, p, s, len(self._format_section(section))))
                X.append(section["embedding"])

        # X = rows of data X 1536
        X = np.array(X)
        embedding = self._get_emb(text)

        # num rows of data X 1
        o = X @ embedding
        l  = [(v, i) for i, v in enumerate(o)]
        l.sort(key=lambda x: x[0])

        # Handle any control flow flags
        for flag in ControlFlowFlags:
            for prompt in self.ctrl_flow_prompts[flag]:
                if embedding @ prompt > l[-1][0]:
                    return sections, ControlFlowFlags.REFER_PREVIOUS
    
        # Sort sections based on relevance
        sorted = []
        for i in range(len(sections)):
            sorted.append(sections[l[-(i+1)][1]])
        return sorted, None

    def _compile_convo(self):
        """
        Compiles the conversation buffer into a string.
        """
        s = ""
        for c in self.conversation_buffer:
            s += c + "\n"
        return s

    # Not calling since this adds latency
    def _get_database(self):
        """
        Returns the database.
        """

        MONGODB_URL = os.getenv("MONGODB_URL")
        client = MongoClient(MONGODB_URL)
        return client['chatassist-development']

    def _add_log_db(self):
        """
        Adds the conversation log to the database
        """
        print(self.id)
        self.db.ConversationLog.update_one({"_id": ObjectId(self.id)}, {"$set": {"conversation": self.conversation_buffer, "domain": self.domain}}, upsert=True)
        print(self.conversation_buffer)

