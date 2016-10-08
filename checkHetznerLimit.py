import requests
import json
import sys
import os
from calendar import monthrange
from datetime import date
from slackclient import SlackClient
if __name__ == '__main__':
    settingsPara = ""
    try:
        settingsPara =  sys.argv[1]
    except IndexError:
    	print("Error: Parameter Settings missing")
    	pass

    try:
        #Lese settings.json
        with open(settingsPara) as settings_file:
        	settings = json.load(settings_file)

        serverIP = settings["hetzner"]["ipAddress"]
        user = settings["hetzner"]["user"]
        passwd= settings["hetzner"]["password"]
        trafficLimit = settings["hetzner"]["trafficLimit"]
        hostname = settings["hetzner"]["hostname"]
        #Slackbot 
        #Chanel in dem die Notification angezeigt wird
        chan=settings["slack"]["channel"]
        #API Key https://api.slack.com
        token = settings["slack"]["token"]
        #Text der Notification
        message = settings["slack"]["message"]
        
        DateBeginn = str(date.today().year) + "-" + str(date.today().month) + "-" + "01"
        DateEnd = str(date.today().year) + "-" + str(date.today().month) + "-" + str(monthrange(date.today().year, date.today().month)[1])

        parameter = {'type':'month','from':DateBeginn,'to':DateEnd,'ip':serverIP}

       	url = 'https://robot-ws.your-server.de/traffic'
        r = requests.post(url, auth=(user, passwd), data=parameter)
        jsonData = json.loads(r.text)

        trafficOut = int(round(jsonData['traffic']['data'][serverIP]['out'],0))
        trafficIn  = int(round(jsonData['traffic']['data'][serverIP]['in'],0))
        trafficSum = int(round(jsonData['traffic']['data'][serverIP]['sum'],0))
        
        notificationtext=""

        #Warngrenzen prüfen
        if (trafficOut >= int(trafficLimit)):
        	if not os.path.exists(hostname + ".json"):
        		with open(hostname + ".json", 'w') as lastmessagefile:
        			json.dump({"lastmessage": date.today().month -1}, lastmessagefile)

        	with open(hostname + ".json", 'r') as lastmessagefile:    
        		jsonLastmessage = json.load(lastmessagefile)
        	
        	if(jsonLastmessage["lastmessage"] != date.today().month):
	        	notificationtext += 'Out:'
	        	notificationtext += str(trafficOut)
	        	#notificationtext += 'MB | In:'
	        	#notificationtext += str(trafficIn)
	        	#notificationtext += 'MB | Sum:'
	        	#notificationtext += str(trafficSum)
	        	notificationtext += 'MB | Limit:'
	        	notificationtext += str(trafficLimit)
	        	notificationtext += 'MB'
        		with open(hostname + ".json", 'w') as lastmessagefile:
        			json.dump({"lastmessage": date.today().month}, lastmessagefile)
	        	message += notificationtext
	        	#print(message)
	        	sc = SlackClient(token)
	        	slackResponse= str(sc.api_call("chat.postMessage", as_user="true:", channel=chan, text=message))
	        	print(slackResponse)
	        	if (slackResponse.find("error") == -1):
	        		print("Message successfully transmitted to Slack.")
	        	else:
	        		print("Message could not be transmitted to Slack")

    except OSError as err:
        print("OS error: {0}".format(err))
        pass