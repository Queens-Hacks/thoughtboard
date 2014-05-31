import os


from twilio.rest import TwilioRestClient
 
# Your Account Sid and Auth Token from twilio.com/user/account


client = TwilioRestClient(os.environ.get('ACCOUNT_SID'), os.environ.get('AUTH_TOKEN'))
 
message = client.messages.create(body="Jenny please?! I love you <3",
    to=os.environ.get('CELL_NUM'),    # Replace with your phone number
    from_="+14378002675") # Replace with your Twilio number
print message.sid