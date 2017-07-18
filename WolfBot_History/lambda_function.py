import math
import sys
import dateutil.parser
import datetime
import time
import os
import logging
import csv
#import urllib.request
from yahoo_finance import Share
#experimental
import matplotlib
matplotlib.use('agg',warn=False, force=True)
from matplotlib import pyplot as plt
from imgurpython import ImgurClient




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


""" --- Helper Functions --- """

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


def validate_action_WolfBot_History(symbol, start_date, end_date):
    #validate the action of WolfBot_History, if there are missing slots then elicit them

    if symbol == (None or ""):
        return build_validation_result(False, 'symbol', 'Please state a symbol. E.g. $AMZN')

    if (start_date is None) or (not isvalid_date(start_date)):
        return build_validation_result(False, 'start_date', 'Please state start date. E.g. {}'.format(datetime.date.today() - datetime.timedelta(days=30)))   #display a start date 30 days prior
    elif datetime.datetime.strptime(start_date, '%Y-%m-%d').date() >= datetime.date.today():        #can't go into the future
        return build_validation_result(False, 'start_date', 'Please pick a date in the past. E.g. 16/06/2017')

    if (end_date is None) or not (isvalid_date(end_date)):
        return build_validation_result(False, 'end_date','Please state end date. E.g. {}'.format(datetime.date.today()))
    elif (datetime.datetime.strptime(end_date, '%Y-%m-%d').date() > datetime.date.today()) \
            or (datetime.datetime.strptime(end_date, '%Y-%m-%d').date() < datetime.datetime.strptime(start_date,'%Y-%m-%d').date()):  # can't go into the future and before the start date
        return build_validation_result(False, 'end_date', 'Please pick a date after the start date. E.g. 16/06/2017')

    return build_validation_result(True, None, None)



""" --- Functions that control the bot's behavior --- """


def action_WolfBot_History(intent_request):
    """
    Performs dialog management and fulfillment for doing stock history
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    symbol = get_slots(intent_request)['symbol']

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

    #using last days method, force values into intent_request
    try:
        if get_slots(intent_request)['days'] is not None:
            get_slots(intent_request)['start_date'] = str(datetime.date.today() - datetime.timedelta(days=int(get_slots(intent_request)['days'])))
            get_slots(intent_request)['end_date'] = str(datetime.date.today())
    except KeyError:
        pass

    start_date = get_slots(intent_request)['start_date']
    end_date = get_slots(intent_request)['end_date']

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
                      'content': 'Closing3... {} {} {} {}'.format(symbol, start_date, end_date, sys.exc_info()[0])})




    #start sussing it out
    if source == "DialogCodeHook":
        #determine the symbol
        symbol = get_slots(intent_request)['symbol']
        # Using date questioning method (default)
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        validation_result = validate_action_WolfBot_History(symbol, start_date, end_date)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

    #scrub out the dollar symbol - why is this everywhere? because I don't know what keeps adding the $ back into symbol lol

    if '$' in symbol:
        symbol = symbol.strip('$')

    symbol_result_history = Share(symbol)
    try:
        symbol_result = lookup2(symbol)
        symbol_history = symbol_result_history.get_historical2(start_date, end_date)
    except:
        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Closing4... Try again with a valid symbol. E.g. $AMZN'})

    #formatting
    trade_time = symbol_result["trade_time"].split(" UTC"); trade_time = trade_time[0]

    #building the content to deliver
    content = ""
    #build with first day and last day
    content = "{} starts at {:.2f} on {} and ends at {:.2f} on {}".format(
        symbol, float(symbol_history[0]["Adj_Close"]), symbol_history[0]["Date"],
        float(symbol_history[-1]["Adj_Close"]), symbol_history[-1]["Date"]
    )


    #staging imgur client - use https://api.imgur.com/oauth2/addclient
    client_id = 'GET_YOUR_OWN'
    client_secret = 'GET_YOUR_OWN'
    client = ImgurClient(client_id, client_secret)

    # filter the output
    output_filter = []
    for element_dict in symbol_history:
        output_filter.append({k: element_dict[k] for k in element_dict.keys() & {'Date', 'Adj_Close'}})

    # set up X data
    X_date = []
    for element_dict in output_filter:
        X_date.append(element_dict['Date'])

    # set up Y data
    Y_close = []
    for element_dict in output_filter:
        Y_close.append(element_dict['Adj_Close'])

    # use xticks because matplotlib doesn't like strings
    plt.plot(Y_close)
    plt.xticks(range(len(X_date)), X_date)
    plt.title("{} Starts: {} Ends: {}".format(symbol, start_date, end_date))

    #make sure its empty
    try:
        os.remove('/tmp/foo.png')
    except:
        pass
    #save, generate, delete
    plt.savefig('/tmp/foo.png')
    callback = client.upload_from_path("/tmp/foo.png", config=None, anon=True)
    imgur_link = callback['link']
    plt.gcf().clear()
    os.remove('/tmp/foo.png')

    '''
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': content + "  " + imgur_link})
    '''
    #using response card
    response = {
        "sessionAttributes": intent_request["sessionAttributes"],
        "dialogAction": {
            "type": "Close",
            'fulfillmentState': "Fulfilled",
            "message": {
                "content": "Showing ${} between {} and {}".format(symbol_result["symbol"], start_date, end_date),
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
                        "imageUrl": "{}".format(imgur_link),
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
    if intent_name == 'WolfBot_HistoryC':
        return action_WolfBot_History(intent_request)

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
