# Chores 🧹
I currently live in a house with two other people. Between our schedules and general forgetfulness, it gets hard to coordinate who has cleaned what, or when it was cleaned. Our solution to this was a "chore chart", which is - you guessed it - a chart on the wall listing our chores, names, and dates. 

It works fine, but presents a fun use case for specific libraries in python, so I thought I'd try to automate/simplify the process. 

## Setup 
First I created a Google Sheet, and manually entered the tasks assigned to each roommate for that week - to be used as a baseline for the next steps in the process. The structure of the table is as follows: 

| Date          | PERSON 1      | PERSON 2      | PERSON 3      |
| ------------- | ------------- |------------- |------------- |
| Week Start Date | Task         |Task         |Task         |


I imported the necessary modules using the following block of code: 
```
import pandas as pd # DataFrame manipulation
import os.path # accessing token file/credentials 
from google.auth.transport.requests import Request # sending requests to server
from google.oauth2.credentials import Credentials # working with API token
from google_auth_oauthlib.flow import InstalledAppFlow # handling client credentials
from googleapiclient.discovery import build # building request container/service
from googleapiclient.errors import HttpError # API Error handling
from itertools import permutations # creating combinations for task assignment 
from random import randrange # selection of random indexes 
import datetime as dt
import smtplib # emails 
from email.message import EmailMessage # emails
```

## Fetching Data
The Google Sheets API documentation included instructions on fetching sheets using the sheet ID. I made slight modifications to the code + placed it in a function `get_past_week()` which grabs the data from its source. The function returns each row as a list, then places those lists within a list. As a result, creating a dataframe makes the header columns into the first row of the dataset. My remedy to this issue was the `first_row_header()` function, which takes the contents of the first row + makes them into the column names for the dataframe. 


## Determining Task Order
Next, using the `next_task_set()` function, I create a permutation based on the three available "Tasks" which refer to the grouping of areas in the house that need cleaning: Kitchen, Landing, Dining. The permutation from the most recent entry is then excluded from the possible options. A random integer between 0 - `len(list_of_permutations)` is generated using `randrange`. This integer is used to determine which of the permutations will be used in the next week. 

The new task order, along with the start date and respective asignees will be added to the google sheet, and used as the baseline for the next week's order (i.e, exclude that order from consideration before assigning new tasks).

## Notifications 
Each roommate's name + email is stored in a list. This list is used within the function `email_tasks(contact_info, sender, roomies)`, which does as its name suggests: emails each roommate with their respective task for the week. This function includes some error handling in the form of local text files. When the script is run, a text file is created with a "Success" or "Failure" title. I recieve notifications when the folder has been updated, and will be able to determine its status by looking at the file name. 

# Maintenance + Next Steps 
- Currently working on a limitation brought up by Outlook, switching emails to gmail, keeping gmail api use consistent 
- Organizing code further using classes
