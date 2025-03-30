#!/usr/bin/env python
 
# import normal packages
import platform 
import logging
import sys
import os
import sys
if sys.version_info.major == 2:
    import gobject
else:
    from gi.repository import GLib as gobject
import sys
import time
import requests # for http GET
import configparser # for config/ini file
 
# our own packages from victron
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '/opt/victronenergy/dbus-systemcalc-py/ext/velib_python'))
from vedbus import VeDbusService


class DbusGensetGenericService:
  def __init__(self, servicename, paths, productname='generic-genset', connection='MQTT external data update'):
    config = self._getConfig()
    deviceinstance = int(config['DEFAULT']['Deviceinstance'])
    customname = config['DEFAULT']['CustomName']
    productname = config['DEFAULT']['ProductName']

    self._dbusservice = VeDbusService("{}.generic_{:02d}".format(servicename, deviceinstance),register=False)
    self._paths = paths
    
    logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))
    
    paths_wo_unit = [
      '/StatusCode', # 0=Standby; 1..7=Startup; 8=Running; 9=Stopping; 10=Error
      '/Start'
    ]
    
    # Create the management objects, as specified in the ccgx dbus-api document
    self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
    self._dbusservice.add_path('/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())
    self._dbusservice.add_path('/Mgmt/Connection', connection)
    
    # Create the mandatory objects
    self._dbusservice.add_path('/DeviceInstance', deviceinstance)
    self._dbusservice.add_path('/ProductId', 45126) # ID of a DSE generator - will enable engine readings and icon in VRM
    self._dbusservice.add_path('/ProductName', productname)
    self._dbusservice.add_path('/CustomName', customname)    
    self._dbusservice.add_path('/FirmwareVersion', 0, writeable=True)
    self._dbusservice.add_path('/Serial', "00000000", writeable=True)
    self._dbusservice.add_path('/HardwareVersion', 0, writeable=True)
    self._dbusservice.add_path('/Connected', 1)
    self._dbusservice.add_path('/UpdateIndex', 0)
    self._dbusservice.add_path('/RemoteStartModeEnabled', 1)
    self._dbusservice.add_path('/NrOfPhases', 3)
    self._dbusservice.add_path('/EnableRemoteStartMode', 1)
    self._dbusservice.add_path('/Role', "genset")
    
    # add paths without units
    for path in paths_wo_unit:
      self._dbusservice.add_path(path, None, writeable=True)
    
    # add path values to dbus
    for path, settings in self._paths.items():
      self._dbusservice.add_path(
        path, settings['initial'], gettextcallback=settings['textformat'], writeable=True, onchangecallback=self._handlechangedvalue)

    # register the service
    self._dbusservice.register()

    # last update
    self._lastUpdate = 0
    
    # add _signOfLife 'timer' to get feedback in log every 5minutes
    gobject.timeout_add(self._getSignOfLifeInterval()*60*1000, self._signOfLife)
 
  def _getConfig(self):
    config = configparser.ConfigParser()
    config.read("%s/config.ini" % (os.path.dirname(os.path.realpath(__file__))))
    return config
 
 
  def _getSignOfLifeInterval(self):
    config = self._getConfig()
    value = config['DEFAULT']['SignOfLifeLog']
    
    if not value: 
        value = 0
    
    return int(value)
  
  def _signOfLife(self):
    logging.info("--- Start: sign of life ---")
    logging.info("Last _update() call: %s" % (self._lastUpdate))
    logging.info("Last '/Ac/Power': %s" % (self._dbusservice['/Ac/Power']))
    logging.info("--- End: sign of life ---")
    return True
 
 
  def _handlechangedvalue(self, path, value):
  
    # Add actions based on changed values here

    # Returning True to accept the change
    return True

def main():
  #configure logging
  logging.basicConfig(      format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO,
                            handlers=[
                                logging.FileHandler("%s/current.log" % (os.path.dirname(os.path.realpath(__file__)))),
                                logging.StreamHandler()
                            ])
 
  try:
      logging.info("Start")
  
      from dbus.mainloop.glib import DBusGMainLoop
      # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
      DBusGMainLoop(set_as_default=True)
     
      #formatting 
      _kwh = lambda p, v: (str(round(v, 2)) + 'kWh')
      _hz = lambda p, v: (str(round(v, 1)) + 'Hz')
      _a = lambda p, v: (str(round(v, 1)) + 'A')
      _w = lambda p, v: (str(round(v, 1)) + 'W')
      _v = lambda p, v: (str(round(v, 1)) + 'V')
      _degC = lambda p, v: (str(v) + '°C')
      _s = lambda p, v: (str(v) + 's')
     
      #start our main-service
      pvac_output = DbusGensetGenericService(
        servicename='com.victronenergy.genset',
        paths={
          # comment out parameters that your system does not have
          #  then they will appear as a dash instead of 0
          '/Ac/L1/Power': {'initial': 0, 'textformat': _w},
          '/Ac/L2/Power': {'initial': 0, 'textformat': _w},
          '/Ac/L3/Power': {'initial': 0, 'textformat': _w},
          '/Ac/L1/Current': {'initial': 0, 'textformat': _a},
          '/Ac/L2/Current': {'initial': 0, 'textformat': _a},
          '/Ac/L3/Current': {'initial': 0, 'textformat': _a},
          '/Ac/L1/Voltage': {'initial': 0, 'textformat': _v},
          '/Ac/L2/Voltage': {'initial': 0, 'textformat': _v},
          '/Ac/L3/Voltage': {'initial': 0, 'textformat': _v},
          '/Ac/Power': {'initial': 0, 'textformat': _w},
          '/Ac/Frequency': {'initial': 0, 'textformat': _hz},
          '/Ac/Energy/Forward': {'initial': 0, 'textformat': _kwh},
          '/Engine/CoolantTemperature': {'initial': 0, 'textformat': _degC}
        }
        )
     
      logging.info('Connected to dbus, and switching over to gobject.MainLoop() (= event based)')
      mainloop = gobject.MainLoop()
      mainloop.run()            
  except Exception as e:
    logging.critical('Error at %s', 'main', exc_info=e)
if __name__ == "__main__":
  main()
