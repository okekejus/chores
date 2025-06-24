# Chores 🧹
I currently live in a house with two other people. Between our schedules and general forgetfulness, it gets hard to coordinate who has cleaned what, or when it was cleaned. Our solution to this was a "chore chart", which is - you guessed it - a chart on the wall listing our chores, names, and dates. 

It works fine, but presents a fun use case for specific libraries in python, so I thought I'd try to automate/simplify the process. I initially tried to set this up using a hotmail account, but was forced to switched to gmail due to a number of authentication issues I ran into with Microsoft. 

## Setup 
I began by creating an app within the Google Console, gathering the app details (Client ID, Client Secret, tokens etc.) and storing them in my .env file. 

Next, I created a Google Sheet, and manually entered the tasks assigned to each roommate for that week - to be used as a baseline for the next steps in the process. The structure of the table is as follows: 

| Date          | PERSON 1      | PERSON 2      | PERSON 3      |
| ------------- | ------------- |------------- |------------- |
| Week Start Date | Task         |Task         |Task         |


I imported the necessary modules using the following block of code: 
```
import pandas as pd 
import os
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
from dotenv import load_dotenv
from tasks import * # importing classes for the chores created in a separate script.
import base64
from email.message import EmailMessage

```

## Fetching Data
The Google Sheets API documentation included instructions on fetching sheets using the sheet ID. I made slight modifications to the code + placed it in a function `fetch_past_week()` which grabs the data from its source. The function returns each row as a list, then places those lists within a list. As a result, creating a dataframe makes the header columns into the first row of the dataset. My remedy to this issue was the `first_row_header()` function, which takes the contents of the first row + makes them into the column names for the dataframe. 

## Chore Class 
I created a class called `Chore` with attributes such as `section` and `task` which provide the name of the area (Kitchen, Dining, Landing), as well as the associated tasks to be completed. 

## Determining Task Order
Next, using the `next_task_set()` function, I create a permutation based on the area names (Chore.section). The most recent assignment is excluded from the list of permutations. A random integer between 0 - `len(list_of_permutations)` is generated using `randrange`. This integer is used to determine which of the permutations will be used in the next week. 

The new task order, along with the start date and respective asignees are added to the sheet using the `update_spreadsheets()` function, which uses the `format_values()` and `rownum()` functions to insert the values into their rightful positions. This will allow them to be used as the baseline for the next week's order (i.e, exclude that order from consideration before assigning new tasks).


## Notifications 
Using the new task order, classes, and a dict containing each house mate's name & email, I run the `send_mail(sender, recipient_name, recipient_email, chore)` function, which tells everyone what they should be doing. This is set to run once a week on my personal desktop. 

# Maintenance + Next Steps 
- Need to update google sheet with determined task order
- set up response system + logging when a task has been completed
