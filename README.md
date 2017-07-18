# WolfBot, your stock market companion

WolfBot is your personal stock market companion on Slack! It can fetch your stock information, provide trending data and keep an eye on your watchlist. All done via Natural Language Processing (provided by AWS Lex).

# Add to your Slack channels
<a href="https://slack.com/oauth/authorize?&client_id=136639530325.213401704019&scope=bot,chat:write:bot,team:read,im:history,channels:history"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>

## Demo

[Youtube Demo Video](https://youtu.be/qLd8xrJMaSc)

Note: This is my submission for [AWS Chatbot Challenge](https://aws.amazon.com/blogs/aws/announcing-the-aws-chatbot-challenge-create-conversational-intelligent-chatbots-using-amazon-lex-and-aws-lambda/)

## Current Features:

## Spotcheck
WolfBot can fetch stock information for you when you enter the stock symbol.

![Spotcheck](http://i.imgur.com/RBAPwCE.png)

## Historical Trend
WolfBot will able to show you historical data and plot it as a trend graph.

![lastdays](http://i.imgur.com/JZpBBxg.png)

It can even take precise dates.

![between](http://i.imgur.com/WvHWS1s.png)


## Watchlist

Wolfbot can even help you keep track of your portfolio by sniffing out your watchlist.

You can add a symbol to the list

![add](http://i.imgur.com/zzneOGx.png)

Or delete one.

![delete](http://i.imgur.com/0vzUVLD.png)

And display your watchlist!

![show](http://i.imgur.com/7tIoyaZ.png)


## Help
If you ever get stuck, just type in "Help Me" for random tips!

![help1](http://i.imgur.com/4PpyJDd.png)

![help2](http://i.imgur.com/3OgNCka.png)

## Deployment Instructions
[Click here](./Deployment.md)



## Dev Stack

1.	Python 3.6
2.	Slack API
3.	query.yahooapis.com

## AWS Services Used
1.	AWS Lex
2.	AWS Lambda
3.	AWS DynamoDB
4.	S3 Bucket


## Architecture
![Architechture](./WolfBot_Chatbot_Architecture.png)
