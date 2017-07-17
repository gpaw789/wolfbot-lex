# coding=utf-8
import time
import os, sys
import logging
import json
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import WolfBot_Spotcheck




logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def build_content(userid):
    # essentials
    dynamodb = boto3.resource("dynamodb", region_name='us-east-1',
                              endpoint_url='https://dynamodb.us-east-1.amazonaws.com')
    table = dynamodb.Table('watchlist')

    # making sure that the user exists
    try:
        response = table.get_item(
            Key={
                'userid': userid
            }
        )
        item = response['Item']
        print("GetItem succeeded:")
        print(json.dumps(item, indent=4, cls=DecimalEncoder))
        content = "Existing User detected."

    except:

        response = table.put_item(
            Item={
                'userid': userid,
                'symbol_list': []
            }
        )
        print("PutItem succeeded:")
        print(json.dumps(response, indent=4, cls=DecimalEncoder))
        content = "New user detected. Watchlist created."

    # making sure that the symbol_list exists
    try:
        response = table.query(
            KeyConditionExpression=Key('userid').eq(userid)
        )
        symbol_list = []
        for i in response['Items']:
            symbol_list = i['symbol_list']  # doesn't matter, the list in Item should only be one item

        content = ""
        for symbol in symbol_list:
            content = "{} >> {}".format(content, spotcheck(symbol))

    except KeyError:  # symbol_list doesn't exists
        content = "No symbols in watchlist"

    if content is (None or ""):
        content = "No symbols in watchlist"

    return content

def spotcheck(symbol):
    #scrub out the dollar symbol - why is this everywhere? because I don't know what keeps adding the $ back into symbol lol

    if '$' in symbol:
        symbol = symbol.strip('$')

    try:
        symbol_result = WolfBot_Spotcheck.lookup2(symbol)
        trade_time = symbol_result["trade_time"].split(" UTC"); trade_time = trade_time[0]
        return "{} {} {} {} ({}) {}".format(
            symbol_result["name"], symbol_result["symbol"],
            symbol_result["price"],symbol_result["change"],
            symbol_result["pc_change"], trade_time)
    except:
        return "Unexpected error:", sys.exc_info()[0]





""" --- Functions that control the bot's behavior --- """


def action_WolfBot_Watchlist_Show(intent_request):
    """
    Performs dialog management and fulfillment for doing stock history
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    source = intent_request['invocationSource']

    #build content
    content = build_content(intent_request["userId"])


    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': content})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'WolfBot_Watchlist_Show':
        return action_WolfBot_Watchlist_Show(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')





""" --- Main handler --- """



def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
