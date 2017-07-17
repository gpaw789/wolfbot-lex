# coding=utf-8
import time
import os, sys
import logging
import json
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
#import WolfBot_Spotcheck




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

def add_symbol(userid, symbol):
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

    except:

        response = table.put_item(
            Item={
                'userid': userid,
                'symbol_list': []
            }
        )
        print("PutItem succeeded:")
        print(json.dumps(response, indent=4, cls=DecimalEncoder))

    # making sure that the symbol_list exists
    try:
        response = table.query(
            KeyConditionExpression=Key('userid').eq(userid)
        )
        symbol_list = []
        for i in response['Items']:
            symbol_list = i['symbol_list']  # doesn't matter, the list in Item should only be one item

        if symbol not in symbol_list:
            response = table.update_item(
                Key={
                    'userid': userid,
                },
                UpdateExpression="set symbol_list = list_append(symbol_list,:sl)",  # appending to list
                ExpressionAttributeValues={
                    ':sl': [symbol]
                },
                ReturnValues="UPDATED_NEW"
            )

            print("UpdateItem succeeded:")
            print(json.dumps(response, indent=4, cls=DecimalEncoder))
        else:
            return 2


    except KeyError:  # symbol_list doesn't exists
        response = table.update_item(
            Key={
                'userid': userid,
            },
            UpdateExpression="set symbol_list = :sl",
            ExpressionAttributeValues={
                ':sl': [symbol]
            },
            ReturnValues="UPDATED_NEW"
        )

    return 0






""" --- Functions that control the bot's behavior --- """


def action_WolfBot_Watchlist_Add(intent_request):
    """
    Performs dialog management and fulfillment for doing stock history
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    #code borrowed from WolfBot_Spotcheck
    slots = get_slots(intent_request)

    symbol = get_slots(intent_request)['symbol']    #even if you put the slot in the utter, it will always read none


    #get symbol data
    if symbol is None:
        try:
            utter = intent_request["inputTranscript"]

        except:
            utter = "This is empty"

        #extract symbol from utter
        try:
            #break the string into a list, and then pick the one with the $ symbol
            phrase_list = utter.split(" ")
            for element in phrase_list:
                if "$" in element:
                    symbol_manual = element.strip("$")
                    get_slots(intent_request)['symbol'] = symbol_manual     #force the value in, this allows to break out of the strict slot criteria
                    symbol = symbol_manual

                else:
                    symbol = ""
        except:                  #if there's no element, aka no check $
            return close(intent_request['sessionAttributes'],
                         'Fulfilled',
                         {'contentType': 'PlainText',
                          'content': 'Closing1... Try again with a valid symbol. E.g. $AMZN'})

    # prepping the values
    symbol = get_slots(intent_request)['symbol']

    #get the code, 0 = success, 1 = error, 2 = existing
    success_code = add_symbol(intent_request["userId"], symbol)

    #building content
    if success_code == 0:
        content = "You have successfully added {} to your watchlist. " \
                    "Type \"Show me my watchlist\".".format(symbol)
    elif success_code == 2:
        content = "{} is already on your watchlist. Type \"Show my watchlist\".".format(symbol)
    else:
        content = "Failed to add {} to your watchlist. Please try again or type \"Help Me\".".format(symbol)

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
    if intent_name == 'WolfBot_Watchlist_Add':
        return action_WolfBot_Watchlist_Add(intent_request)

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
