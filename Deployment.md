## Deployment

This guide assumed that the user has basic knowledge of AWS.

Before we start:
1. Create an AWS account.
2. Create a DynamoDB table. e.g. Table Name: UserList, Primary Key: UserId (string). Copy the ARN.
3. Create a use role in IAM, e.g. WolfBotRole. Policies required:
    (a)AWSLambdaCloudFormationExecutionRole-451abaae-4200-49ce-a2d6-05c307188f3b
    (b)AWSLambdaDynamoDBExecutionRole
    (c)AWSLambdaBasicExecutionRole-d06f5640-5258-4a5e-ad9f-f569ce14e8e4
    Attach Role Policy from DynamoDB ARN from Step (2)
4. Download each WolfBot function folder. Ensure that the required python modules are in the WolfBot root folder*. [Helpful links](http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
5. Zip the WolfBot function folders invidivually. Ensure that the lambda_function.py is at the root of the zip file.
6. Upload to Amazon S3. Take note of each link.
7. Start creating a lambda function for each for the folder below. Configure the settings below:
    Runtime: Python 3.6
    Handler: lambda_function.lambda_handler
    Existing role: service-role/WolfBotRole
    Memory (MB): 128
    Timeout: 3 sec
8. In each lambda function, use code entry type: Upload a file from Amazon S3. This is where the S3 links come into play. Upload accordingly.
9. Use the test scripts from test_scripts and make sure that they work.
10. Create a custom bot from Lex.
11. Create each intent for each WolfBot function, keep the same name for continuity.
12. Use the diagrams provided as a guide for each intent and how it is configured. Generally the Lambda init and fulfillment are taken care by the its lambda function.
13. Once everything is tested and working, build the and publish to slack API. [Helpful Link](http://docs.aws.amazon.com/lex/latest/dg/slack-bot-association.html)


*Some modules have been pre-configured in the WolfBot function folders

# WolfBot Help

Function will randomly generate a tip

# WolfBot Spotcheck

Function utilised a modified [yahoo-finance](https://github.com/gpaw789/yahoo-finance) python module.
Returns a response card. So it may look funny in testing page. Use slack to see the proper response.

# WolfBot History

IMPORTANT: AWS Lambda is built using a special linux AMI, that means whatever python modules you download will compile using Linux.
Usually this is not an issue, however it is known that matplotlib and numpy will use a different compiled C files, which cause the function to stop working.
You will know when you get this message: Importing the multiarray numpy extension module failed.  Most likely you are trying to import a failed build of numpy
Workaround by downloading the modules using an EC2, stuff it in the function folder and upload to S3. Yes, this also mean it is a pain for testing.

Due to the yahoo shutting down its API, I had to build a [workaround](https://github.com/gpaw789/yahoo-finance) to query the data from another source, but that source require a web cookie.
The process goes: 1. get symbol, 2. get cookie/crumbs, 3. scan the csv output, 4. plot on graph, 5. upload to imgur
Therefore there is substantial delays getting the results. Sometimes the cookie/crumbs are not valid and have to re-try.
Before of this, the Memory and Timeout is recommended setting to 192 mb and 30 seconds

You will need your own imgur client id, get it here https://api.imgur.com/oauth2/addclient

# WolfBot Watchlist Add

Remember to change to your endpoint_url and table name

# WolfBot Watchlist Delete

Remember to change to your endpoint_url and table name

# WolfBot Watchlist Show

Remember to change to your endpoint_url and table name
Re-use the WolfBot_Spotcheck.py function here