# ShellyEMPlugin
#
# Author: Iqas
# Based in ShellyCloudPlugin by mario-peters
#

"""
<plugin key="ShellyEMPlugin" name="Shelly EM Plugin" author="Iqas" version="1.0.0" wikilink="https://github.com/iqas/ShellyEMPlugin/wiki" externallink="https://github.com/iqas/ShellyEMPlugin">
    <description>
        <h2>Shelly EM Plugin</h2><br/>
        Plugin for controlling Shelly EM devices.
        <h3>Configuration</h3>
        <ul style="list-style-type:square">
            <li>IP Address is the IP Address of the Shelly device. Default value is 127.0.0.1</li>
            <li>Username is a optional user on shelly local web</li>
            <li>Password is a optional password on shelly local web</li>
            <li>Model is the type of Shelly EM device you want to add. Shelly EM or Shelly 3EM</li>
            <li>Batery Meter is the clamp number connected to battery line(optional) </li>
            <li>Grid meter is the clamp number connected to the grid line. The grid type divide produced and returned </li>
        </ul>
        <br/><br/>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Username" label="Username" width="200px" />
        <param field="Password" label="Password" width="200px" password="true"/>
        
        <param field="Mode1" label="Type" width="200px" required="true">
            <options>
               <option label="Shelly EM" value="SHEM2"/>
               <option label="Shelly 3EM" value="SHEM3"/>
            </options>
        </param>
        <param field="Mode5" label="Battery meter" width="200px" required="true">
            <options>
               <option label="Meter 1" value="1"/>
               <option label="Meter 2" value="2"/>
               <option label="Meter 3" value="3"/>
               <option label="None" value="0"/>
            </options>
        </param>

        <param field="Mode6" label="Grid meter" width="200px" required="true">
            <options>
               <option label="Meter 1" value="1"/>
               <option label="Meter 2" value="2"/>
               <option label="Meter 3" value="3"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import requests
import json

class BasePlugin:
 
    total1 = 0
    total_returned1 = 0
    total2 = 0
    total_returned2 = 0
    total3 = 0
    total_returned3 = 0
    name1="Meter-1"
    name2="Meter-2"
    name3="Meter-3"
    name_relay="Relay"
    type = "2"
    grid = 1
    battery = 0
    
    def __init__(self):
        return

    def onStart(self):
        Domoticz.Log("onStart called")
        Domoticz.Log("Len Devices: "+str(len(Devices)))
        Domoticz.Heartbeat(30)
        
        if (Parameters["Mode1"].strip()  == "SHEM3"): self.type = "3"
        if (Parameters["Mode6"].strip()  == "1"): self.grid = 1
        elif (Parameters["Mode6"].strip()  == "2"): self.grid = 2
        elif (Parameters["Mode6"].strip()  == "3"): self.grid = 3
        
        if (Parameters["Mode5"].strip()  == "1"): self.battery = 1
        elif (Parameters["Mode5"].strip()  == "2"): self.battery = 2
        elif (Parameters["Mode5"].strip()  == "3"): self.battery = 3
        

        
        if len(Devices) == 0:
            try:
                headers = {'content-type':'application/json'}
                response_shelly = requests.get("http://"+Parameters["Address"]+"/status",headers=headers, auth=(Parameters["Username"], Parameters["Password"]), timeout=(10,10))
                try:
                    json_items = json.loads(response_shelly.text)
                except Exception as e:
                    Domoticz.Error("Error json parse: "+str(e))
                    return
                response_shelly.close()
                createSHELLYEM(self, json_items)
            except requests.exceptions.Timeout as e:
                Domoticz.Error(str(e))

    def onStop(self):
        Domoticz.Log("onStop called")
        
    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        if Parameters["Mode1"] == "SHEM3" or Parameters["Mode1"] == "SHEM2":
            
            headers = {'content-type':'application/json'}
            url = "http://"+Parameters["Address"]
            if str(Command) == "On":
                Devices[91].Update(nValue=1,sValue="On")
                url = url + "/relay/0?turn=on" 
            if str(Command) == "Off":
                Devices[91].Update(nValue=1,sValue="Off")
                url = url + "/relay/0?turn=off"
            try:
                response = requests.get(url,headers=headers, auth=(Parameters["Username"], Parameters["Password"]), timeout=(10,10))
                Domoticz.Debug(response.text)
                response.close()
            except requests.exceptions.Timeout as e:
                Domoticz.Error(str(e))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        headers = {'content-type':'application/json'}
        try:
            request_shelly_status = requests.get("http://"+Parameters["Address"]+"/status",headers=headers, auth=(Parameters["Username"], Parameters["Password"]), timeout=(10,10))
        except requests.exceptions.Timeout as e:
            Domoticz.Error(str(e))
        Domoticz.Debug(request_shelly_status.text)
        try:
            json_request = json.loads(request_shelly_status.text)
        except Exception as e:
            Domoticz.Error("Error json parse: "+str(e))
            return
        updateSHELLYEM(self, json_request)
        request_shelly_status.close()

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def createSHELLYEM(self, json_request):
    Domoticz.Log("Creating meters")
    # Meters
    Domoticz.Device(Name=self.name1 + "_power", Unit=11, Used=1, Type=248, Subtype=1).Create()
    Domoticz.Device(Name=self.name2 + "_power", Unit=12, Used=1, Type=248, Subtype=1).Create()
    if (self.type == "3"):
        Domoticz.Device(Name=self.name3 + "_power", Unit=13, Used=1, Type=248, Subtype=1).Create()
    # Totals
    Domoticz.Device(Name=self.name1 + "_kWh", Unit=21, Used=1, Type=243, Subtype=29).Create()
    Domoticz.Device(Name=self.name2 + "_kWh", Unit=22, Used=1, Type=243, Subtype=29).Create()
    if (self.type == "3"):
        Domoticz.Device(Name=self.name3 + "_kWh", Unit=23, Used=1, Type=243, Subtype=29).Create()
    Domoticz.Log("Creating relays")
    #Total returned
    Domoticz.Device(Name="Returned" + "_kWh", Unit=24, Used=1, Type=243, Subtype=29).Create()
    # Total Solar
    Domoticz.Device(Name="Produced" + "_kWh", Unit=25, Used=1, Type=243, Subtype=29).Create()
    # Total Consumed
    Domoticz.Device(Name="Grid_Consumed" + "_kWh", Unit=26, Used=1, Type=243, Subtype=29).Create()
    if (self.battery != "0"):
        # Battery Charged
        Domoticz.Device(Name="Battery_Charged" + "_kWh", Unit=27, Used=1, Type=243, Subtype=29).Create()
        # Battery Discharged
        Domoticz.Device(Name="Battery_Discharged" + "_kWh", Unit=28, Used=1, Type=243, Subtype=29).Create()
    #Relay
    Domoticz.Device(Name=self.name_relay , Unit=91, Used=1, Type=244, Subtype=73).Create()
        
    # Update values
    self.total1 = json_request['emeters'][0]['total']
    self.total_returned1 =  json_request['emeters'][0]['total_returned']
    self.total2 = json_request['emeters'][1]['total']
    self.total_returned2 =  json_request['emeters'][1]['total_returned']
    if (self.type == "3"):
        self.total3 = json_request['emeters'][2]['total']
        self.total_returned3 =  json_request['emeters'][2]['total_returned']

def updateSHELLYEM(self, json_request):
    #1
    meterpower1 = json_request['emeters'][0]['power']
    if (self.type == "3"): meterpf1 =  json_request['emeters'][0]['pf']
    if (self.type == "3"): metercurrent1 =  json_request['emeters'][0]['current']
    metervoltage1 =  json_request['emeters'][0]['voltage']
    meterenergy1 = json_request['emeters'][0]['total']
    meterenergy_returned1 = json_request['emeters'][0]['total_returned']
    
    #2
    meterpower2 = json_request['emeters'][1]['power']
    if (self.type == "3"): meterpf2 =  json_request['emeters'][1]['pf']
    if (self.type == "3"): metercurrent2 =  json_request['emeters'][1]['current']
    metervoltage2 =  json_request['emeters'][1]['voltage']
    meterenergy2 = json_request['emeters'][1]['total']
    meterenergy_returned2 = json_request['emeters'][1]['total_returned']

    #3
    if (self.type == "3"):
        meterpower3 = json_request['emeters'][2]['power']
        meterpf3 =  json_request['emeters'][2]['pf']
        metercurrent3 =  json_request['emeters'][2]['current']
        metervoltage3 =  json_request['emeters'][2]['voltage']
        meterenergy3 = json_request['emeters'][2]['total']
        meterenergy_returned3 = json_request['emeters'][2]['total_returned'] 

    self.total1 = json_request['emeters'][0]['total']
    self.total_returned1 =  json_request['emeters'][0]['total_returned']
    self.total2 = json_request['emeters'][1]['total']
    self.total_returned2 =  json_request['emeters'][1]['total_returned']
    if (self.type == "3"):
        self.total3 = json_request['emeters'][2]['total']
        self.total_returned3 =  json_request['emeters'][2]['total_returned']
    #Relay
    relay = json_request['relays'][0]['ison']

    
# Update meters
    #Power
    Devices[11].Update(nValue=0, sValue=str(meterpower1))
    Devices[12].Update(nValue=0, sValue=str(meterpower2))
    Devices[13].Update(nValue=0, sValue=str(meterpower3))
    #Total
    Devices[21].Update(nValue=0,sValue=str(meterpower1)+";"+str(self.total1))
    Devices[22].Update(nValue=0,sValue=str(meterpower2)+";"+str(self.total2))
    Devices[23].Update(nValue=0,sValue=str(meterpower3)+";"+str(self.total3))
    
    if (self.grid  == 1): 
        if (meterpower1 < 0): Devices[26].Update(nValue=0,sValue=str(0)+";"+str(self.total1))
        else : Devices[26].Update(nValue=0,sValue=str(meterpower1)+";"+str(self.total1))
        if (meterpower1 >= 0): Devices[24].Update(nValue=0,sValue=str(0)+";"+str(self.total_returned1))
        else : Devices[24].Update(nValue=0,sValue=str(meterpower1*-1)+";"+str(self.total_returned1))
        if (self.battery == 0):
            if (self.type == "3"):
                produced = meterpower2 + meterpower3
                produc_kwh = self.total2 + self.total3
            else:
                produced = meterpower2
                produc_kwh = self.total2
        else : 
            if (self.battery == 2):
                produced = meterpower3
                produc_kwh = meterenergy3
                if (meterpower2 < 0): 
                    Devices[27].Update(nValue=0,sValue=str(meterpower2)+";"+str(meterenergy_returned2))
                    Devices[28].Update(nValue=0,sValue=str(0)+";"+str(meterenergy2))
                else :
                    Devices[28].Update(nValue=0,sValue=str(meterpower2)+";"+str(meterenergy2))
                    Devices[27].Update(nValue=0,sValue=str(0)+";"+str(meterenergy_returned2))

                Devices[25].Update(nValue=0,sValue=str(produced)+";"+str(produc_kwh))
            if (self.battery == 3 and self.type == "3"):
                produced = meterpower2
                produc_kwh = meterenergy2
                if (meterpower3 < 0): 
                    Devices[27].Update(nValue=0,sValue=str(meterpower3)+";"+str(meterenergy_returned3))
                    Devices[28].Update(nValue=0,sValue=str(0)+";"+str(meterenergy3))
                else :
                    Devices[28].Update(nValue=0,sValue=str(meterpower3)+";"+str(meterenergy3))
                    Devices[27].Update(nValue=0,sValue=str(0)+";"+str(meterenergy_returned3))
        Devices[25].Update(nValue=0,sValue=str(produced)+";"+str(produc_kwh))
    elif (self.grid  == 2):
        if (meterpower2 < 0): Devices[26].Update(nValue=0,sValue=str(0)+";"+str(self.total2))
        else : Devices[26].Update(nValue=0,sValue=str(meterpower2)+";"+str(self.total2))
        if (meterpower2 >= 0): Devices[24].Update(nValue=0,sValue=str(0)+";"+str(self.total_returned2))
        else : Devices[24].Update(nValue=0,sValue=str(meterpower2*-1)+";"+str(self.total_returned2))
        if (self.battery == 0): 
            if (self.type == "3"):
                produced = meterpower1 + meterpower3
                produc_kwh = self.total1 + self.total3
            else:
                produced = meterpower1
                produc_kwh = self.total1
        else : 
            if (self.battery == 1):
                produced = meterpower3
                produc_kwh = meterenergy3
                if (meterpower1 < 0): 
                    Devices[27].Update(nValue=0,sValue=str(meterpower1)+";"+str(meterenergy_returned1))
                    Devices[28].Update(nValue=0,sValue=str(0)+";"+str(meterenergy1))
                else :
                    Devices[28].Update(nValue=0,sValue=str(meterpower1)+";"+str(meterenergy1))
                    Devices[27].Update(nValue=0,sValue=str(0)+";"+str(meterenergy_returned1))

            if (self.type == "3" and self.battery == 3):
                produced = meterpower1
                produc_kwh = meterenergy1
                if (meterpower3 < 0): 
                    Devices[27].Update(nValue=0,sValue=str(meterpower3)+";"+str(meterenergy_returned3))
                    Devices[28].Update(nValue=0,sValue=str(0)+";"+str(meterenergy3))
                else :
                    Devices[28].Update(nValue=0,sValue=str(meterpower3)+";"+str(meterenergy3))
                    Devices[27].Update(nValue=0,sValue=str(0)+";"+str(meterenergy_returned3))

        Devices[25].Update(nValue=0,sValue=str(produced)+";"+str(produc_kwh))

    if (self.grid  == 3 and self.type == "3"):
        if (meterpower3 < 0): Devices[26].Update(nValue=0,sValue=str(0)+";"+str(self.total3))
        else : Devices[26].Update(nValue=0,sValue=str(meterpower3)+";"+str(self.total3))
        if (meterpower3 >= 0): Devices[24].Update(nValue=0,sValue=str(0)+";"+str(self.total_returned3))
        else : Devices[24].Update(nValue=0,sValue=str(meterpower3*-1)+";"+str(self.total_returned3))
        if (self.battery == 0):
            produced = meterpower1 + meterpower2
            produc_kwh = self.total1 + self.total2 
        else : 
            if (self.battery == 1):
                produced = meterpower2
                produc_kwh = meterenergy2
                if (meterpower1 < 0): 
                    Devices[27].Update(nValue=0,sValue=str(meterpower1)+";"+str(meterenergy_returned1))
                    Devices[28].Update(nValue=0,sValue=str(0)+";"+str(meterenergy1))
                else :
                    Devices[28].Update(nValue=0,sValue=str(meterpower1)+";"+str(meterenergy1))
                    Devices[27].Update(nValue=0,sValue=str(0)+";"+str(meterenergy_returned1))

            if (self.battery == 2):
                produced = meterpower1
                produc_kwh = meterenergy1
                if (meterpower2 < 0): 
                    Devices[27].Update(nValue=0,sValue=str(meterpower2)+";"+str(meterenergy_returned2))
                    Devices[28].Update(nValue=0,sValue=str(0)+";"+str(meterenergy2))
                else :
                    Devices[28].Update(nValue=0,sValue=str(meterpower2)+";"+str(meterenergy2))
                    Devices[27].Update(nValue=0,sValue=str(0)+";"+str(meterenergy_returned2))

        Devices[25].Update(nValue=0,sValue=str(produced)+";"+str(produc_kwh))
        
    # Update relays
    if (relay == True):
        Devices[91].Update(nValue=1, sValue="On")
    else:
        Devices[91].Update(nValue=0, sValue="Off")
    
