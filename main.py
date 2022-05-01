# contact: biduradhikari@gmail.com

from __future__ import print_function

from datetime import datetime, timezone, timedelta, date
import os.path
from tkinter import *
from tkcalendar import *
import sys
import dateutil.parser as parser
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# variable placeholders
yearmonth = ['Year(BS)', 'Baisakh', 'Jestha', 'Asadh', 'Shrawan', 'Bhadra', 'Asoj', 'Kartik', 'Mangsir', 'Poush', 'Magh', 'Falgun', 'Chaitra']
entries = [] # this is where the widget writes values supplied

# Google API things follow
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            curr_dir = os.path.dirname(os.path.realpath(__file__))
            credential_file = str(curr_dir) + '/credentials.json'
            flow = InstalledAppFlow.from_client_secrets_file(
                credential_file, SCOPES)
            creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        try:
            global service
            service = build('calendar', 'v3', credentials=creds)

# Google API things done

            # the main activities happen now:
            global cal_list, cal_ID_list
            cal_list = []
            cal_ID_list = []
            list_cal() # makes lists of calendar name and ID in the signed in account
            pick_calendar() # you choose which calendar to write dates in
            pick_new_year() # you pick where to start
            ask_number_of_days_per_month() # ask number of days
            write_nepali_dates() # final step
            next_new_year = int(entries[0])+1 # for the dialog box
            print("Success!" + "\n Completed with no warnings. \n New year of "+str(next_new_year)+ " is on " + today + ". Check if that's true!")
            sys.exit()
        except HttpError as error:
            print('An error occurred: %s' % error)


def list_cal():
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        cal_list.append(calendar_list_entry['summary'])
        cal_ID_list.append(calendar_list_entry['id'])
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break

def pick_calendar():
    win = Tk()
    win.geometry("200x300")
    win.title("Select calendar")
    variable = StringVar(win)
    w = OptionMenu(win, variable, *cal_list)
    w.config(width=25)
    w.pack()

    def ok():
        selected_cal = variable.get()
        global selected_cal_id
        for index, i in enumerate(cal_list):
            if i == selected_cal:
                selected_cal_id = cal_ID_list[index]
        win.destroy()

    button = Button(win, text="Select calendar above\n Then click here.", command=ok)
    button.pack()
    mainloop()

def pick_new_year():
    win= Tk()
    win.title("When is the Nepali new year?")
    win.geometry("700x600")
    cal= Calendar(win, selectmode="day")
    cal.config(font=("Arial", 25))
    cal.pack(pady=10)
    def obtain_date():
        global date
        date = parser.parse(cal.get_date())
        win.destroy()
    button= Button(win, text= "Select the Date", command= obtain_date)
    button.pack(pady=20)
    win.mainloop()

def ask_number_of_days_per_month():
    def search():
        j = 0
        for element in entries:
            entries[j]=element.get()
            j += 1
        win.destroy()

    win= Tk()
    win.title("Days/month")
    win.geometry("200x400")

    for i in range(13):
        label = Label(win, text=yearmonth[i])
        label.grid(row=i, column=0)
        entry = Entry(win, width=5)
        entry.grid(row=i, column=1)
        entries.append(entry)

    button1 = Button(win, text="Ok", command=search)
    button1.grid(row=14, column=0)
    win.mainloop()

def write_nepali_dates():
    new_year_day = date.astimezone().isoformat()
    global today
    today = new_year_day.replace("T00:00:00+05:45", "")
    for i in range(12):
        index = i+1
        month = yearmonth[index]
        for day in range(int(entries[index])):
            todayDate = datetime.strptime(today, "%Y-%m-%d")
            tomorrow1 = todayDate + timedelta(days=1)
            tomorrow = str(tomorrow1)
            tomorrow = tomorrow.replace(" 00:00:00", "")
            day += 1
            title = str(day)+" "+month+" "+str(entries[0])
            event = {
                'summary': title,
                'start': {
                    'date': today,
                    'timeZone': 'Asia/Kathmandu',
                },
                'end': {
                    'date': tomorrow,
                    'timeZone': 'Asia/Kathmandu',
                },
                'transparency' : 'transparent',
            }
            event = service.events().insert(calendarId=selected_cal_id, body=event).execute()
            today = tomorrow


if __name__ == '__main__':
    main()
