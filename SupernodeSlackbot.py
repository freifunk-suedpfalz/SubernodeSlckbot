import json
import requests
import sys
from slackclient import SlackClient

def get_supernode(nodesjson):
    supernodes = [[],[]]
    #loop over every node and check if node is gateway
    for node in list(nodesjson['nodes']):
        try:
            if nodesjson['nodes'][node]['flags']['gateway'] == True:
                if not nodesjson['nodes'][node]['nodeinfo']['node_id'] in supernodes:
                    supernodes[0].append(nodesjson['nodes'][node]['nodeinfo']['node_id'])
                    supernodes[1].append(nodesjson['nodes'][node]['nodeinfo']['hostname'])
        except:
            pass
    return supernodes

def get_nodes(nodesjson, gatewayID):
    nodes = []
    #loop over every node and check if the node is connected to the specified gateway
    for node in list(nodesjson['nodes']):
        try:
            if nodesjson['nodes'][node]['statistics']['gateway'] == gatewayID:
                if not nodesjson['nodes'][node]['nodeinfo']['node_id'] in nodes:
                    nodes.append(nodesjson['nodes'][node]['nodeinfo']['node_id'])
        except:
            pass
    return nodes

if __name__ == '__main__':
    try:
        #Lese settings.json
        with open('settings.json') as settings_file:    
            settings = json.load(settings_file)

        #Warngrenze für Notifications
        critical_threshold = settings["nodesjson"]["threshold"]
        #URL der nodes.json
        url = settings["nodesjson"]["url"]
        #Slackbot 
        #Chanel in dem die Notification angezeigt wird
        chan=settings["slack"]["channel"]
        #API Key https://api.slack.com
        token = settings["slack"]["token"]
        #Text der Notification
        message = settings["slack"]["message"]
        
        notificationtext = ""
        threshold_reached = False
        sumNodes = 0
        
        #Lade nodes.json vom Server
        resp = requests.get(url=url)
        data = json.loads(resp.text)
        
        #Gateway informationen sammeln, die NodeID wird für get_nodes ermittelt
        supernodeData = get_supernode(data)
        #supernodeData[0] -> NodeID
        #supernodeData[1] -> Hostname

        #Summe der verbundenen Nodes ermitteln
        for value in range(0,len(supernodeData[0])):
            sumNodes += len(get_nodes(data,supernodeData[0][value]))


        for value in range(0,len(supernodeData[0])):
            countNodes = len(get_nodes(data,supernodeData[0][value]))
            percetNodes = int(round((100/sumNodes)*countNodes,0))
            notificationtext += supernodeData[1][value] #Hostname des Gateway
            notificationtext += ' ('
            notificationtext += supernodeData[0][value] #NodeID des Gateway                
            notificationtext += ')'                
            notificationtext += ' = '
            notificationtext += str(countNodes) #Anzahl der verbundenen Nodes
            notificationtext += " Nodes -> "
            notificationtext += str(percetNodes) #Prozentanzeige
            notificationtext += "%\n"
            #Warngrenzen prüfen
            if (percetNodes >= critical_threshold):
                threshold_reached = True

        print(notificationtext)
        #Notification auslösen wenn Grenzwerte überschritten sind
        if (threshold_reached == True):
            print("Slackbot message -> send")
            message += notificationtext
            sc = SlackClient(token)
            print(sc.api_call("chat.postMessage", as_user="true:", channel=chan, text=message))
    except OSError as err:
        print("OS error: {0}".format(err))
        pass
    except:
        print("Unexpected error:", sys.exc_info()[0])
        pass
