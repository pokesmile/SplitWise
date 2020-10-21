from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


def main():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../../credentials/credential'
                                              '.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API to fetch INBOX
    results = service.users().messages()\
        .list(userId='pokesmile87@gmail.com',
              labelIds=['Label_680880215095427487']).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
    else:
        print("Curve Receipts:")
        for message in messages:
            msg = service.users().messages()\
                .get(userId='pokesmile87@gmail.com', id=message['id'])\
                .execute()
            if is_curve_receipt(msg):
                last_receipt_date = open("last_receipt.txt", "w+")
                receipt = get_metadata_from(get_subject(msg), get_date(msg))
                if len(last_receipt_date.read()) > 0:
                    time = last_receipt_date.read()
                    if is_new_receipt(receipt, time):
                        last_receipt_date.write(receipt['date'])
                        return receipt
                else:
                    last_receipt_date.write(receipt['date'])
                    return receipt


def is_new_receipt(receipt, time):
    if receipt['date'] > time:
        return True
    return False


def get_date(msg):
    for headers in msg['payload']['headers']:
        if headers['name'] == 'Date':
            return headers['value']


def get_subject(msg):
    for headers in msg['payload']['headers']:
        if headers['name'] == 'Subject':
            return headers['value']


def is_curve_receipt(msg):
    for headers in msg['payload']['headers']:
        if headers['name'] == 'Subject' and headers['value'] \
                .startswith('Curve Receipt: '):
            return True


def get_metadata_from(subject, date):
    trimmed_subject = subject.replace("Curve Receipt: Purchase at ", "")
    place = trimmed_subject[:trimmed_subject.index(" on ")]
    without_place = trimmed_subject.replace(place + " on ", "")
    time = without_place[:without_place.index(" for ")]
    without_place_and_time = without_place.replace(time + " for ", "")
    amount = without_place_and_time.split()[0]
    currency = without_place_and_time.split()[1]

    print("Place: " + place + ", Date: " + date + ", Amount: " + amount +
          ", Currency: " + currency)

    return \
        {"place": place, "date": date, "amount": amount, "currency": currency}


if __name__ == '__main__':
    main()

