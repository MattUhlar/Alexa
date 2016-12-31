import requests
import json

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

    if intent_name == "DisplayPage":
        return display_page(intent_request)
    else:
        raise ValueError('Invalid intent')

def handleFinishSessionRequest(intent, session):
    """Called before ending the session"""
    card_title = "Goodbye"
    speech_output = "There you go" 
    reprompt_text = "There you go"
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
    speech_output = "I am ready to assist"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ("I am ready to assist")
    should_end_session = False

    speechlet_response = build_speechlet_response(card_title, speech_output,reprompt_text, should_end_session)    
    return build_response(session_attributes, speechlet_response)

def display_page(intent):
    website_name = intent['intent']['slots']['Website']['value']
    url = 'https://www.' + website_name + '.com'
    data = {'url': url, 'create_new_tab': True}
    r = requests.post('http://50.159.106.72:5000/display_page', json=data)
    return get_success_response()

def get_success_response():
    """Builds Alexa's response after successful request"""

    session_attributes = {}
    card_title = "Sent"
    speech_output = "There you go"
    reprompt_text = "There you go"
    should_end_session = True

    speechlet_response = build_speechlet_response(card_title, speech_output,reprompt_text, should_end_session)    
    return build_response(session_attributes, speechlet_response)

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
