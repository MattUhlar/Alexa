import praw
import random
import os
from twilio.rest import TwilioRestClient

# TWILIO API CREDENTIALS
TWILIO_SID=os.environ['TWILIO_SID']
TWILIO_AUTH_TOKEN=os.environ['TWILIO_AUTH_TOKEN']
TWILIO_ACCOUNT_NUMBER=os.environ['TWILIO_ACCOUNT_NUMBER']

# REDDIT API CREDENTIALS
REDDIT_CLIENT_ID=os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET=os.environ['REDDIT_CLIENT_SECRET']
REDDIT_USERNAME=os.environ['REDDIT_USERNAME']
REDDIT_PASSWORD=os.environ['REDDIT_PASSWORD']
REDDIT_USER_AGENT=os.environ['REDDIT_USER_AGENT']

TWILIO_CONTACT_LIST={'CONTACTS GO HERE'}

REDDIT_MEME_SUBREDDITS = [
    'meirl',
    'me_irl',
    'dankmemes',
    'adviceanimals',
    'memes',
    'memeeconomy'
]

# Initialize Twilio client
twilio = TwilioRestClient(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Initialize Reddit client
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT,
                     username=REDDIT_USERNAME,
                     password=REDDIT_PASSWORD)


# --------------- Entry Point ------------------
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest, etc.) 
    The JSON body of the request is provided in the event parameter.
    """

    session = event['session']
    request = event['request'] 
    event_type = event['request']['type']
    request_id = event['request']['requestId']

    if session['new']:
        on_session_started({'requestId': request_id}, session)

    if event_type == 'LaunchRequest':
        return on_launch(request, session)
    elif event_type == 'IntentRequest':
        return on_intent(request, session)
    elif event_type == 'SessionEndedRequest':
        return on_session_ended(request, session)

# --------------- Functions that control the skill's state changes ------------------
def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    # add cleanup logic here

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    # Dispatch to your skill's launch
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent['name']

    if intent_name == "SendDankMeme":
        return send_dank_meme()
    else:
        raise ValueError('Invalid intent')

def handleFinishSessionRequest(intent, session):
    """Called before ending the session"""
    card_title = "Goodbye"
    speech_output = "Enjoy your meme" 
    reprompt_text = "Enjoy your meme"
    should_end_session = True

    speechlet_response = build_speechlet_response(card_title, speech_output,reprompt_text, should_end_session)    
    return build_response(session_attributes, speechlet_response)

# --------------- Functions that control the skill's behavior ------------------
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Ask me for a dank meme."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ("I didn't catch that. Ask me for a dank meme.")
    should_end_session = False

    speechlet_response = build_speechlet_response(card_title, speech_output,reprompt_text, should_end_session)    
    return build_response(session_attributes, speechlet_response)

def get_success_response():
    """Builds Alexa's response after successful request"""

    session_attributes = {}
    card_title = "Sent"
    speech_output = "I sent you a dank meme."
    reprompt_text = "I sent you a dank meme."
    should_end_session = True

    speechlet_response = build_speechlet_response(card_title, speech_output,reprompt_text, should_end_session)    
    return build_response(session_attributes, speechlet_response)

def send_message(contact, message_body):
    """Sends SMS message to contact"""
    twilio.messages.create(to=contact, from_=TWILIO_ACCOUNT_NUMBER, body=message_body)

def get_dank_meme():
    """Returns a 'hot' meme from one of several subreddits"""

    subreddit = random.choice(REDDIT_MEME_SUBREDDITS)
    memes = list(reddit.subreddit(subreddit).hot(limit=25))

    dank_meme = random.choice(memes)
    dank_meme = dank_meme.title + '\n' + dank_meme.url

    return dank_meme

def send_dank_meme():
    """Sends meme title and image to contact"""
    contact = TWILIO_CONTACT_LIST['CONTACT NAME GOES HERE']
    send_message(contact, get_dank_meme())
    return get_success_response()

# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    } 
