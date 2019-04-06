import json
import threading
import requests
import Sheet

# Set the webhook_url to the one provided by Slack when you create the
# webhook at https://my.slack.com/services/new/incoming-webhook/
webhook_url = 'https://hooks.slack.com/services/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'
# queuing
# webhook_url = 'https://hooks.slack.com/services/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'
# #shepherd-bot-testing

def notify_queueing(match_num):
    send_plain_message("Match number "+str(match_num)+" is ending.")

def team_numbers_on_deck(b1, b2, g1, g2):
    send_plain_message("The following teams are now on deck: \n On the blue side\
, we have team #%i and team #%i \n On the gold side, we\
 have team #%i and team #%i" % (b1, b2, g1, g2))

def team_names_on_deck(b1, b2, g1, g2):
    send_plain_message("The following teams are now on deck: \n On the blue side\
, we have %s and %s \n On the gold side, we\
 have %s and %s" % (b1, b2, g1, g2))

def send_plain_message(message):
    slack_data = {'text': message}
    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
        )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

def announce_next_match(match_number):
    thread = threading.Thread(target=next_match_thread, args=(match_number,), daemon=True)
    thread.start()
def next_match_thread(match_number):
    next_match_info = Sheet.get_match(int(match_number) + 1)
    b1name = next_match_info["b1name"]
    b2name = next_match_info["b2name"]
    g1name = next_match_info["g1name"]
    g2name = next_match_info["g2name"]
    team_names_on_deck(b1name, b2name, g1name, g2name)
