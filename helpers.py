from datetime import datetime, timedelta
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

import nltk
#import speech_recognition as sr

import requests
import random
from bs4 import BeautifulSoup

import os
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def createGoogleEvent(activity):
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=scopes)
    credentials = flow.run_console()

    pickle.dump(credentials, open("token.pkl", "wb"))

    credentials = pickle.load(open("token.pkl", "rb"))

    service = build("calendar", "v3", credentials=credentials)

    result = service.calendarList().list().execute()

    calendar_id = result['items'][0]['id']

    events = service.events().list(calendarId=calendar_id, timeZone="Asia/Kolkata").execute()

    start_time = datetime(2020, 12, 31, 19, 30, 0)
    end_time = start_time + timedelta(hours=1.5)
    timezone = 'Asia/Kolkata'

    event = {
      'summary': 'Workout',
      'location': 'Hyderabad',
      'description': '',
      'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timezone,
      },
      'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timezone,
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    service.events().insert(calendarId=calendar_id, body=event).execute()

def speechRecognizer():

    speech_recognized = []

#    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say the activity you want to input and its priority(High/Low) Ex.Workout under High Priority")
        audio = recognizer.listen(source)

    speech = recognizer.recognize_google(audio)
    tokens = nltk.word_tokenize(speech.lower())

    high = True
    for value in tokens:
        if value == low:
            high = False

    def priority(high):
        return 'High' if high == True else 'Low'

    result_priority = priority(high)
    Activity = tokens[0]
    Priority = result_priority
    Speech = speech

    speech_recognized.append(Activity)
    speech_recognized.append(Priority)
    speech_recognized.append(speech)

    return speech_recognized


tasks = "Meditation, run, Socialize, Workout, Study"

matched = []


def getTime(tasks):

    activities = nltk.word_tokenize(tasks)

    for activity in activities:

        url = 'https://www.google.com/search?q=when+is+the+most+ideal+time+to+'+activity+'&rlz=1C1CHBF_enIN932IN932&oq=When+&aqs=chrome.0.69i59l3j69i57j0i67i395i457j69i61l3.2148j1j1&sourceid=chrome&ie=UTF-8'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')

        result = soup.find('div', class_="LGOjhe")

        if result is not None:

            sentence = str(result.text).lower()
            words = nltk.word_tokenize(sentence)
            matched.append(activity)

            for i in range(len(words)):
                if words[i] =='am' or words[i] =='pm' or words[i] =='a.m.' or words[i] =='p.m.':
                    matched.append(words[i-1] + words[i])
                elif words[i] =='morning' or words[i] =='afternoon' or words[i] =='evening' or words[i] =='night' or words[i] == 'sunrise' or words[i] == 'sunset':
                    matched.append(words[i])

    if matched is not None:
        return matched

Timings = getTime(tasks)

# act = []

# for activity in activities:
#     if activity in Timings:
#         act.append(activity)

# print(act)

# def getTime2(Timings, sleep, act):

#     times = []
#     for i in range(len(Timings)):
#         for each_character in Timings[i]:
#             if each_character.isdigit():
#                 times.append(Timings[i])



# for i in range(len(Timings)):
#     if Timings[i] == act[0] or Timings[i] == act[1] or Timings[i] == act[2] or Timings[i] == act[3]:
#         if not Timings[i+1] == None or Timings[i+1] == act[0] or Timings[i+1] == act[1] or Timings[i+1] == act[2] or Timings[i+1] == act[3] or Timings[i+1] == act[4]:
#             act.remove(Timings[i])
#             new_time = getTime2(Timings, sleep, act)


