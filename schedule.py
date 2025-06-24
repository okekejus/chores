import pandas as pd 
import os
from google.auth.transport.requests import Request # Google api modules, used to call various services within network (sheets, gmail)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from itertools import permutations # creating permutations of tasks on the chore list 
from random import randrange # used for order selection
import datetime as dt
import smtplib # used for email sending/construction
from email.message import EmailMessage
from email import errors
from dotenv import load_dotenv # env file loading 
from tasks import * # importing classes for the chores created in a separate script.
import base64 # encoding and decoding emails before sending 






def first_row_header(df): 
    """Turn first row of dataset into column names. Used within the fetch_past_week() function. """
    try:
        df.columns = df.iloc[0] # set names of columns to the contents of the first row 
        df = df[1:] # deletes the first row 
        return df
    except Exception as e: 
        print(f"{e}")


def fetch_past_week(SPREADSHEET_ID, SAMPLE_RANGE_NAME, creds): 
    """ Gets the past week's worth of data, to be used for comparison in determining the next set of tasks for the list of contacts."""
    try: 
        service = build("sheets", "v4", credentials=creds) # Calling Sheets API 
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute())
        values = result.get("values", [])
        if not values: 
            return("No data found.") 
        else: 
            values = first_row_header(pd.DataFrame(values))
            values = list(values.tail(1).iloc[0, 1:])
            return values
    except Exception as e: 
        print(f"Error during initial request: {e}")


def rownum(): 
    """ Used to set up the rows for the next entry"""
    try: 
        service = build("sheets", "v4", credentials=creds) # Calling Sheets API 
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute())
        values = result.get("values", [])
        if not values: 
            return "No data found." 
        else: 
            values = first_row_header(pd.DataFrame(values))
            values = values.shape[0] + 2
            return values
    except Exception as e: 
            return f"Error during initial request: {e}"



def next_task_set(most_recent, task_list = ["Kitchen", "Dining", "Landing"]): 
    """ Determines the order of tasks to be completed in the next week, using the past week's task as a reference. """    
    new_order = []
    combs_new = [list(x) for x in permutations(task_list)]

    for item in combs_new: 
        if combs_new == most_recent: 
            pass
        else: 
            new_order.append(item)

    new_index = randrange(0, len(new_order))

    tba =  new_order[new_index]
    return tba

def send_mail(sender, recipient_name, recipient_email, chore, creds):
    """ Sends emails to housemates, including the details for each chore (housed within Chore class)"""
    try: 
        service = build("gmail", "v1", credentials=creds)
        wkstrt = dt.date.today()

        message = EmailMessage()
        task_list = "\n".join(chore.tasks)
        combined = f"Hey {recipient_name}, your tasks for the week of {wkstrt} are below: \n" + task_list + "\nWhen completed, please respond with 'Done'"


        message.set_content(combined)

        message["To"] = recipient_email
        message["From"] = sender
        message["Subject"] = f"{recipient_name}'s Task for week of {wkstrt}: {chore.section}"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw" : encoded_message}

        send_message = (service.users().messages().send(userId="me", body=create_message).execute())

        print(f'Message Id: {send_message["id"]}')
    except Exception as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message

def format_values(week, tba):
        starter = [week]
        for task in tba.values(): 
            starter.append(task)
        values = [starter]
        return values
    
def update_spreadsheets(spreadsheet_id, range_name, value_input_option, _values):
    """ Used to update the file with the determined order of tasks for the week."""

    try:
        service = build("sheets", "v4", credentials=creds)
        values = [starter]
        body = {"values": values}
        result = (service.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                        range=range_name, 
                                                        valueInputOption=value_input_option, 
                                                        body=body,).execute())
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except Exception as e: 
        print(f"An error occured: {e}")
        return e


def main():
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    SAMPLE_RANGE_NAME = os.getenv("SAMPLE_RANGE_NAME")
    SCOPE = ["https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/gmail.addons.current.action.compose", 
            "https://www.googleapis.com/auth/gmail.compose"]
    
    creds = None 

    if os.path.exists("token.json"): 
        creds = Credentials.from_authorized_user_file("token.json", SCOPE) # if token file exists, use it and scope for credentials 
    if not creds or not creds.valid: 
        if creds and creds.expired and creds.refresh_token: 
                creds.refresh(Request())
        else: 
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPE)  
            creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token: 
                token.write(creds.to_json())
    

    values = fetch_past_week(SPREADSHEET_ID, SAMPLE_RANGE_NAME, creds=creds) # getting the old order of values
    to_be_assigned = next_task_set(values) # setting the new order of values
    to_be_assigned = {'Person 1': to_be_assigned[0], "Person 2": to_be_assigned[1], "Person 3": to_be_assigned[2]} # adding names to assignments for sending

    for key, value in to_be_assigned.items(): 
        info = {"Person 1": "person1@domain.com", "Person 2": "Person2@domain.com", "Person 3": "Person3@domain.com"}
        sender = "sender@domain.com"

        if value == kitchen.section: 
            try:
                send_mail(sender=sender, recipient_name=key, recipient_email=info.get(key), chore = kitchen, creds=creds)
                print(f"Mail sent to {key}")
            except Exception as e: 
                print(f"An error occurred during sending {e}")

        elif value == landing.section: 
            try: 
                send_mail(sender=sender, recipient_name=key, recipient_email=info.get(key), chore = landing, creds=creds)
                print(f"Mail sent to {key}")
            except Exception as e: 
                print(f"An error occurred during sending {e}")

        elif value == dining.section:
            try:
                send_mail(sender=sender, recipient_name=key, recipient_email=info.get(key), chore = dining, creds=creds)
                print(f"Mail sent to {key}")
            except Exception as e: 
                print(f"An error occurred during sending {e}")
        else: 
            print("No tasks detected")
            
    for_entry = format_values(dt.date.today(), tba) # runs once a week on Sunday
    range_row = rownum()
        
if __name__== "__main__": 
    load_dotenv()
    main()
