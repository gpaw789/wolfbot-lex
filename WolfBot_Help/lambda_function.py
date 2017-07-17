# coding=utf-8
import time
import os, sys
import logging
import random


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """
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




""" --- Functions that control the bot's behavior --- """


def action_WolfBot_Help(intent_request):
    """
    Performs dialog management and fulfillment for doing stock history
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    source = intent_request['invocationSource']

    tip1 = "Spotcheck: Type \"check $AMZN\" to get the latest stock price. Make sure you use the dollar sign $!"
    tip2 = "History: Type \"$AMZN in the last 30 days\" to get the stock trend for Amazon, Inc in the last 30 days."
    tip3 = "History: Type \"history of $AMZN between 2017-06-01 and 2017-06-30\" for ganular dates. Use YYYY-MM-DD for our international friends!"
    tip4 = "Watchlist: Type \"Add $AMZN to watchlist\" to add the symbol to your personal watchlist. You can also remove symbols"
    tip5 = "Watchlist: Type \"Show my watchlist\" to get a overview of your watchlist."
    tip6 = "Spotcheck: Type \"check $AMZN\" to get the latest stock price. Make sure you use the dollar sign $!"


    tips = [tip1, tip2, tip3, tip4, tip5, tip6]


    content = "Hi! My name is WolfBot and I am your personal assistant to the stock market.     " \
                "{}".format(random.choice(tips))


    '''
    content = "User ID = {}".format(intent_request["userId"])
    '''
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
    if intent_name == 'WolfBot_Help':
        return action_WolfBot_Help(intent_request)

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
