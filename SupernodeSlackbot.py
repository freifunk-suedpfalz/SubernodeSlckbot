import json
import requests
import sys
from pprint import pprint
from slackclient import SlackClient

def get_supernode(nodesjson):
    supernodes = [[],[]]
    #loop over every node and check if node is gateway
    for node in list(nodesjson['nodes']):
        try:
            if nodesjson['nodes'][node]['flags']['gateway'] == True:
                #if nodesjson['nodes'][node]['statistics']['uptime']!="":
                    if not nodesjson['nodes'][node]['nodeinfo']['node_id'] in supernodes:
                        supernodes[0].append(nodesjson['nodes'][node]['nodeinfo']['node_id'])
                        supernodes[1].append(nodesjson['nodes'][node]['nodeinfo']['hostname'])
                        #print(nodesjson['nodes'][node]['flags']['gateway']) 
                        #print(nodesjson['nodes'][node]['nodeinfo']['hostname'])
                        #print(nodesjson['nodes'][node]['statistics']['uptime'])
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
    #Warngrenze für Notifications
    critical_threshold = 50
    #URL der nodes.json
    url = 'https://www.freifunk-suedpfalz.de/karte/nodes.json'
    #Slackbot 
    #Chanel in dem die Notification angezeigt wird
    chan="@simon"
    #API Key https://api.slack.com
    token = "xoxb-xxx"
    #Text der Notification
    warning = "Warnung: Das Verhältniss der Nodes auf den Servern überschreitet die grenzwerte.\n"
    
    try:
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
            warning += notificationtext
            sc = SlackClient(token)
            sc.api_call("chat.postMessage", as_user="true:", channel=chan, text=warning)
    except OSError as err:
        print("OS error: {0}".format(err))
        pass
    except:
        print("Unexpected error:", sys.exc_info()[0])
        pass
