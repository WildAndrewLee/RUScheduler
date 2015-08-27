import json

import flask

from flask import Flask
from flask import render_template

import httplib2

from apiclient import discovery
from oauth2client import client

import datetime

from main import main
import webbrowser

app = flask.Flask(__name__)


@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/donate')
def donate():
    try:
        return render_template('donate.html')
    except:
        print "Cannot render template"
        return "Error with rendering template"

@app.route('/authorize', methods=["GET"])
def authorize():
  if 'credentials' not in flask.session:
    webbrowser.open_new_tab(flask.url_for('oauth2callback'))
    return json.dumps({"success":False})
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    webbrowser.open_new_tab(flask.url_for('oauth2callback'))
    return json.dumps({"success":False})
  else:
    return json.dumps({"success":True})

@app.route('/magic', methods=["POST","GET"])
def magic():
  if flask.request.method=='POST':
    flask.session['JSON']=json.dumps(flask.request.json)
  if 'credentials' not in flask.session:
    # webbrowser.open_new_tab(flask.url_for('oauth2callback'))
    return flask.redirect(flask.url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    # webbrowser.open_new_tab(flask.url_for('oauth2callback'))
    return flask.redirect(flask.url_for('oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http_auth)
    if flask.request.method=='POST':
      print "DATA:\n"
      print flask.request.json
      return main(service, json.dumps(flask.request.json))
    else:
      # print "Didn't get a POST request..."
      # inputDict={"classInfo":[{"subNum":"190","courseNum":"206","sectionNum":"1"}],"school":"NB","reminders":[True,True,True,False]}
      # inputJSON=json.dumps(inputDict)
      return (main(service, flask.session['JSON']))


@app.route('/oauth2callback', methods=["GET"])
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secrets.json',
      scope='https://www.googleapis.com/auth/calendar',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    webbrowser.open_new_tab(auth_uri)
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('magic'), code=307)


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = True 
  app.run()