from datetime import datetime, timedelta
from .models import Connection, User
from . import db
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

#TODO: change this once done testing
# minute tolerance for checking older conninders
TOLERANCE = 10
DEBUG = True

# load secret environment variables
load_dotenv()
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_texts(scheduler):
    ''' Goes through all the sessions and sends texts to the ones who have passed
        their interval time.
    '''
    if DEBUG: print("send_texts called", flush=True)

    with scheduler.app.app_context():
        print("------------- the time is...", datetime.now(), flush=True)

        now = datetime.now()

        this_time = now.time()

        connections = Connection.query.filter(Connection.start_time <= now)
        connections = connections.filter(Connection.end_time >= now)

        for conn in connections:
            if DEBUG: print("> checking connection", conn.id, conn.last_text, conn.interval, this_time, flush=True)

            if conn.last_text + timedelta(minutes=conn.interval) < now:
                if DEBUG: print('>> havent texted yet; texting', conn.id, flush=True)

                # get contact user
                contact = User.query.filter_by(id=conn.contact_id).first()
                
                # get user's phone number
                country_code = contact.country_code
                phone_number = contact.phone_number
                number = country_code + phone_number

                if conn.text_contents == "" or conn.text_contents == None:
                    text_contents = "This is a message from Safe Contact."
                else:
                    text_contents = conn.text_contents

                print('contents:', text_contents)
                client.messages.create(to=TWILIO_NUMBER, from_="+19788785139", body=text_contents)
                
                # set last time to now
                conn.last_text = now

        db.session.commit()
