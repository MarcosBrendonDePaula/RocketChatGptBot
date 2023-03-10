import openai
import os

# Define OpenAI API key 
openai.api_key = os.getenv('OPENAI_API_KEY')
botname = os.getenv('BOT_NAME')
botpassword = os.getenv('BOT_PASS')
botChatName = "@"+os.getenv('BOT_NAME')
server_url = os.getenv('ROCKET_URL')
# Set up the model and prompt


# Generate a response
from pprint import pprint
from random import choice
from threading import Thread
from time import sleep
import json

from rocketchat_API.rocketchat import RocketChat

class RocketChatBot(object):
    def __init__(self, botname, passwd, server, command_character=None):
        self.botname = botname
        self.api = RocketChat(user=botname, password=passwd, server_url=server)
        self.commands = []
        self.auto_answers = []
        self.direct_answers = []
        self.lastts = {}
        self.command_character = command_character

    def get_status(self, auser):
        return self.api.users_get_presence(username=auser)

    def add_dm_handler(self, command, action):
        self.commands.append((command, action))

    def handle_messages(self, messages, channel_id):
        for message in messages['messages']:
            if message['u']['username'] != self.botname:
                for cmd_list in self.commands:
                    cmd_list[1](message)

    def load_ts(self, channel_id, messages):
        if len(messages) > 0:
            self.lastts[channel_id] = messages[0]['ts']
        else:
            self.lastts[channel_id] = ''

    def load_im_ts(self, channel_id):
        response = self.api.im_history(channel_id).json()
        if response.get('success'):
            self.load_ts(channel_id, self.api.im_history(channel_id).json()['messages'])

    def process_messages(self, messages, channel_id):
        try:
            if "messages" in messages:
                if(len(messages['messages'])== 0):
                    return
            if "success" in messages:
                if messages['success'] == False:
                    for im in self.api.im_list().json().get('ims'):
                        self.load_im_ts(im.get('_id'))
                    return
            if len(messages['messages']) > 0:
                self.lastts[channel_id] = messages['messages'][0]['ts']
            self.handle_messages(messages, channel_id)
        except Exception as e:
            pprint(e)
            for im in self.api.im_list().json().get('ims'):
                self.load_im_ts(im.get('_id'))
    
    def process_im(self, channel_id):
        if channel_id not in self.lastts:
            self.lastts[channel_id] = ''
        self.process_messages(self.api.im_history(channel_id, oldest=self.lastts[channel_id]).json(),channel_id)

    def run(self):
        for im in self.api.im_list().json().get('ims'):
                self.load_im_ts(im.get('_id'))
        while 1:
            for im in self.api.im_list().json().get('ims'):
                Thread(target=self.process_im, args=(im.get('_id'),)).start()
            sleep(3)

Contextos = {}
bot = RocketChatBot(botname, botpassword, server_url)

def LimpadorDecontexto():
    pass

def greet(resp):
    user = "@"+resp['u']['username']
    if(user == botChatName):
        return
    
    if(Contextos.get(user) == None):
        Contextos[user] = []
    
    Contextos[user].append({
        "role": "user",
        "content": resp['msg'],
    })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = Contextos[user],
    )

    Contextos[user].append({
        "role": "assistant",
        "content": completion.choices[0].message.content,
    })
    bot.api.chat_post_message(completion.choices[0].message.content, user)

def init():
    bot.add_dm_handler(['gpt'], greet)
    bot.run()
init()