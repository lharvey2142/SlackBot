import os
import time
import re
import urllib.request
import random
from slackclient import SlackClient


slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None


RTM_READ_DELAY = .5
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'
lines = None

def parse_bot_commands(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and not 'subtype' in event:
            wordsincommand = event['text'].split()
            wordsincommandSet = set(wordsincommand)
            #hardcoding this because it would be hard to add to the text file.
            # A seperate text file with commands to pull from a url is probably best option, 
            # but only have 1 of these scenarios so far -lh 2/15
            if wordsincommandSet.intersection({'commit'}):
                data = urllib.request.urlopen('http://whatthecommit.com/index.txt')
                for line in data:
                    response = str(line)
                    response = response[2:-3]
                return response, event['channel']
            responses = searchinput(wordsincommandSet)
            if responses:
                 return responses[random.randrange(0, len(responses))], event['channel']

            
                     
    return None, None

def searchinput(wordsincommandSet):
    for line in lines:
        print(line.split(':')[0].split(';'))
        if wordsincommandSet.intersection(set(line.split(':')[0].split(';'))):
            return line.split(':')[1].split(';')
    return None



def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def printmessage(response, channel):
    slack_client.api_call('chat.postMessage', channel=channel, text=response or default_response)

if __name__ == '__main__':
    if slack_client.rtm_connect(with_team_state=False):
        print('Starter Bot connected and running!')
        # Isolate file reading to only happen when bot connects
        with open('commands.txt') as f:
            lines = f.read().splitlines()
            f.close()
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call('auth.test')['user_id']
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                printmessage(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print('Connection failed. Exception traceback printed above.')
