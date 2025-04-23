import pandas as pd 
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from itertools import permutations
from random import randrange
import datetime as dt
import smtplib
from email.message import EmailMessage
from email import errors

# google API requirements, best stored as .env variables. 
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "insert-id-here"
SAMPLE_RANGE_NAME = "Tasks!A:D"

# Setting up email information for later use
contact_info  = ['email@domain.com', 'email2@domain.com', 'email3@domain.com']
sender = "email@domain.com"
roomies = ["Person 1", "Person 2", "Person 3"]



def get_past_week():
    """ Get file from google sheets."""
    creds = None 

    if os.path.exists("token.json"): 
        creds = Credentials.from_authorized_user_file("token.json", SCOPES) # if token file exists, use it and scope for credentials 
    if not creds or not creds.valid: 
        if creds and creds.expired and creds.refresh_token: 
            creds.refresh(Request())
        else: 
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token: 
                token.write(creds.to_json())
    try: 
        service = build("sheets", "v4", credentials=creds)
        # Calling Sheets API 
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute())
        values = result.get("values", [])
        if not values: 
            print("No data found.")
            return 
        return values
    except HttpError as e: 
        print(f"Error during initial reques: {e}")



def first_row_header(df): 
    """Turn first row of dataset into column names"""
    try:
        df.columns = df.iloc[0] # set names of columns to the contents of the first row 
        df = df[1:] # deletes the first row 
        return df
    except Exception as e: 
        print(f"{e}")


def next_task_set(): 
    """ Determines the order of tasks to be completed in the next week """


    # All possible permutations for the three tasks involved
    combs = permutations(["Kitchen", "Dining", "Landing"])
    combs = list(combs)

    # Get list of tasks 
    tasks = get_past_week()
    tasks = first_row_header(pd.DataFrame(tasks))
    most_recent = list(tasks.tail(1).drop("Date", axis=1).itertuples(index=False, name=None))

    possibilities = list(set(combs) - set(most_recent))

    new_index = randrange(0, len(possibilities))

    tba =  possibilities[new_index]

    person_one = tba[0]
    person_two = tba[1]
    person_three = tba[2]

    new_tasks = pd.DataFrame({"Date": [dt.datetime.today().date()], 
                              "Person 1": [person_one], 
                              "Person 2": [person_two],
                              "Person 3": [person_three]})

    return new_tasks

def post_this_week(spreadsheet_id, spreadsheet_range, value_input_option, new_tasks):
    """This function is used to place the next week's order into the dataset, so it can serve as the baseline for the next week's assignment. The function excludes the most recent task order from the possible assignments for the next week."""
    creds, - = google.auth.default()
    try: 
        service = build("sheets", "v4", credentials=creds)
        new_tasks = new_tasks.tolist()
        body = {"values":new_tasks} 
        result = (service.spreadsheets().values().update(spreadsheetID=spreadsheet_id, 
                                                        range=spreadsheet_range, 
                                                        valueInputOption=value_input_option, 
                                                        body=body).execute()
                 )
        return result 
    except HttpError as error: 
        return error
        




def email_tasks(contact_info, sender, roomies):
    """ Setting up the tasks, their definitions, and the emails for the people they are assigned to. This function will also send out the emails per recipient"""
    
    definitions = ["Sweep + mop \nClean microwave \nWipe surfaces + appliances \nEmpty bins \nToss old food \nWash dish rack pieces \nSpot clean walls if needed", 
                "Sweep + mop + vacuum floors and rugs \nWipe counters + tables + other surfaces \nSpot clean walls if needed \nWash cushion covers + blanket (1-3 times a month depending on use)", 
                "Sweep + mop floors \nWash bath mats \nWipe + scrub toilet bowl, lid etc \nClean vents (once a month) \nClean mirror \nSpot clean walls"]

    zones = ["Kitchen-Laundry-Entrance", "Dining-Living-Rooms", "Bathroom-Landing-Stairs"]
    codes = ["Kitchen", "Dining", "Landing"]

    d = {"code": codes, 
            "zone": zones,
            "definitions": definitions}

    chores = pd.DataFrame(d)

    # Setting up contact information for later 
    

    # determining tasks for Date
    new_row = next_task_set()


    try: 
        post_this_week(new_row) # upload to Google sheets for future reference 
        
        s = smtplib.SMTP("smtp-mail.outlook.com", port=587) # i personally use hotmail, can be changed to something else. 
        s.starttls()
        s.login(sender, "password")
        
        for person, email in zip(roomies, contact_info): 
        # find which task has been assigned + look up definition
            task = new_row[person][0] 
            definition = chores[chores['code']==task]['definitions'].values 

            # creating a plain message
            msg = EmailMessage() 
            content = f"Hey {person}, your task for this week is {task}. It includes the following: {definition}"
            msg.set_content(content)

            # setting sender + recipient
            msg['Subject'] = f"Your Task(s) for {new_row['Date']}"
            msg["From"] = sender
            msg['To'] = email

            # sending message via SMPTP server 
            
            s.send_message(msg)
        s.quit()

        
        with open(f"{new_row['Date']} Success.txt", 'w') as text_file: 
            text_file.write("") # write success file to working directory, will likely update with logger shortly. 
    
    except (email.errors, Exception, smtplib.SMTPException) as e:
        with open(f"{new_row['Date']} Fail.txt", 'w') as text_file: 
            text_file.write("") # write failure file to working directory


def main(): 
    email_tasks()



if __name__ == "__main__":
    main()
