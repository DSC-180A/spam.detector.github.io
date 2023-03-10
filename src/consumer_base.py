import pulsar
import time
import os
import logging
import sys
import csv
import ast
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint as pp
from sentiment_analyzer import sentiment_analyzer

service_account = gspread.service_account(
    filename="config/capstone_googlesheet_key.json")
sheet = service_account.open("capstone abortion tweets")
sample_sheet = sheet.worksheet('sample')


class Consumer(object):
    """
    Create a pulsar producer that writes random messages to a topic
    """

    def __init__(self):
        self.token = os.getenv("ASTRA_STREAMING_TOKEN")
        self.service_url = os.getenv("ASTRA_STREAMING_URL")
        self.subscription = os.getenv("ASTRA_TOPIC")
        self.client = pulsar.Client(self.service_url,
                                    authentication=pulsar.AuthenticationToken(self.token))
        self.consumer = self.client.subscribe(self.subscription, 'tweets')

    def read_messages(self):
        """
        Create and send random messages
        """

        waitingForMsg = True
        while waitingForMsg:
            try:
                msg = self.consumer.receive(1).data().decode('utf-8')

                

                # unload json
                json_response = json.loads(msg)
                tweet_text = json_response['data']['Tweet']

                # analyze sentiment
                sentiment = sentiment_analyzer(tweet_text)

                # add to google sheet
                row = list(ast.literal_eval(msg.decode('utf8')).values())
                sample_sheet.insert_row(row + [sentiment], 2)

                # Acknowledging the message to remove from message backlog
                consumer.acknowledge(msg)
                logging.info(f'received: {msg_text} at {msg_time} with sentiment {sentiment}')

            #waitingForMsg = False
            except:
                print("Still waiting for a message...")
                time.sleep(1)

def read_messages():
    """
    Create an instance of the consumer and
    Fire it up to read messages until the program is terminated
    """
    consumer = Consumer()
    consumer.read_messages()
    consumer.client.close()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO)
    read_messages()
