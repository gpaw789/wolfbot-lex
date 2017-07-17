"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for stocks.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'Orderstocks' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import csv
import urllib.request
from yahoo_finance import Share




logger = logging.getLogger()
logger.setLevel(logging.DEBUG)




""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


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




def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }




""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def lookup2(symbol):

    try:
        share = Share(symbol)
    except:
        return None


    if share.get_name() is None:
        return None

    return {
        "name": share.get_name(),
        "symbol": symbol.upper(),
        "price": share.get_price(),
        "change": share.get_change(),
        "pc_change": share.get_percent_change(),
        "trade_time": share.get_trade_datetime()

    }


def validate_action_WolfBot(symbol_result, symbol):


    if symbol is None:
        return build_validation_result(False,
                                       'symbol',
                                       'Which stock should I lookup?')

    if symbol is not None and symbol is "":
        return build_validation_result(False,
                                       'symbol',
                                       "Symbol is empty")
    if symbol_result is None:
        return build_validation_result(False,
                                       'symbol',
                                       '{} does not exist as a stock symbol, try another. E.g. $AMZN'.format(symbol))

    return build_validation_result(True, None, None)





""" --- Functions that control the bot's behavior --- """


def action_WolfBot(intent_request):
    """
    Performs dialog management and fulfillment for doing stock spotcheck
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
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
    slots = get_slots(intent_request)
    symbol = get_slots(intent_request)['symbol']

    source = intent_request['invocationSource']

    # verify symbol
    try:
        #scrub out the dollar symbol
        if '$' in symbol:
            symbol = symbol.strip('$')
        symbol_result = Share(symbol)
        if symbol_result.get_price() is None:
            return close(intent_request['sessionAttributes'],
                         'Fulfilled',
                         {'contentType': 'PlainText',
                          'content': 'Closing2... {}'.format(symbol)})
    except:
        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Closing3... {} {}'.format(symbol, sys.exc_info()[0])})




    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        symbol = get_slots(intent_request)['symbol']

        validation_result = validate_action_WolfBot(symbol_result,symbol)       #why symbol? because in the other function it needs to tell user it doesn't exist
        if not validation_result['isValid']:        #if its false then run
            slots[validation_result['violatedSlot']] = None     #clear existing slot["something"]
            return close(intent_request['sessionAttributes'],
                         'Fulfilled',
                         {'contentType': 'PlainText',
                          'content': 'Please specify a valid symbol. E.g. $AMZN'})


    #scrub out the dollar symbol - why is this everywhere? because I don't know what keeps adding the $ back into symbol lol

    if '$' in symbol:
        symbol = symbol.strip('$')

    try:
        symbol_result = lookup2(symbol)
    except:
        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Closing4... Try again with a valid symbol. E.g. $AMZN'})


    #formatting
    trade_time = symbol_result["trade_time"].split(" UTC"); trade_time = trade_time[0]
    # currency_symbol = "$"
    # stock_price = currency_symbol + symbol_result["price"]

    # Order the stocks, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    '''
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': '{} {} {} {} {}'
                    .format(symbol_result["symbol"], symbol_result["name"], stock_price,
                    symbol_result["pc_change"],trade_time)})
    '''
    #using response card


    response = {
        "sessionAttributes": intent_request["sessionAttributes"],
        "dialogAction": {
            "type": "Close",
            'fulfillmentState': "Fulfilled",
            "message": {
                "content": "Showing ${}".format(symbol_result["symbol"]),
                "contentType": "PlainText"
            },
            "responseCard": {
                "version": 1,
                "contentType": "application/vnd.amazonaws.card.generic",
                "genericAttachments": [
                    {
                        "title": "{}".format(symbol_result["name"]),
                        "subTitle": "{} {} ({}) {}".format(
                            symbol_result["price"],symbol_result["change"],symbol_result["pc_change"], trade_time),
                        "buttons":[
                            {
                                "text": "Buy",
                                "value": "buy"
                            },
                            {
                                "text": "Sell",
                                "value": "sell"
                            }
                        ]
                    }
                ]
            }
        }
    }

    return response





""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'WolfBot_SpotcheckB':
        return action_WolfBot(intent_request)

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
