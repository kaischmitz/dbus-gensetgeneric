# dbus-wallboxgeneric
Integrate any genset into Victron Energies Venus OS

## Purpose
With the scripts in this repo it should be easily possible to install, uninstall, restart a service that sets up the DBUS structure for any genset in VenusOS and GX devices from Victron.
The idea is to fill this structure later on via MQTT. The genset then shows up in VRM.
Forked from dbus-goecharger by vikt0rm.


## How it works
### Why? ###
I am running a Vestel EVC04 wallbox. It can be controlled via Modbus TCP, however per manufacturer's spec only one single connection to the Modbus instance is allowed.
The entire charging control in my case is running in Nodered which has the connection to the wallbox via Modbus TCP.
So in order to integrate the measured values from the wallbox into the VRM portal I wanted to write the values from my Nodered instance to the Venus OS or VRM directly.

### Details / Process
What is the script doing:
- Running as a service
- connecting to DBus of the Venus OS `com.victronenergy.evcharger.generic_{DeviceInstanceID_from_config}`
- Paths are added to the DBus with default value 0 - including some settings like name, etc
- After that a "loop" is started which can handle updated values by callback - nothing in there yet
- After successful DBus connection all data points need to be updated via MQTT. The coding of the data points is listed in [CCGX-Modbus-TCP-register-list.xlsx](https://github.com/victronenergy/dbus_modbustcp/blob/master/CCGX-Modbus-TCP-register-list.xlsx) in the field list under com.victronenergy.evcharger

## Install & Configuration
### Get the code
Just grap a copy of the main branche and copy them to a folder under `/data/` e.g. `/data/dbus-wallboxgeneric`.
After that call the install.sh script.

The following script should do everything for you:
```
wget https://github.com/kaischmitz/dbus-wallboxgeneric/archive/refs/heads/main.zip
unzip main.zip "dbus-wallboxgeneric-main/*" -d /data
mv /data/dbus-wallboxgeneric-main /data/dbus-wallboxgeneric
chmod a+x /data/dbus-wallboxgeneric/install.sh
/data/dbus-wallboxgeneric/install.sh
rm main.zip
```
⚠️ Check configuration after that - because service is already installed an running and with wrong connection data (host) you will spam the log-file

### Change config.ini
Within the project there is a file `/data/dbus-wallboxgeneric/config.ini` - just change the values - most important is the deviceinstance under "DEFAULT". More details below:

| Section  | Config vlaue | Explanation |
| ------------- | ------------- | ------------- |
| DEFAULT  | SignOfLifeLog  | Time in minutes how often a status is added to the log-file `current.log` with log-level INFO |
| DEFAULT  | Deviceinstance | Unique ID identifying the wallbox in Venus OS |
| DEFAULT  | CustomName | Custom name of the wallbox  |
| DEFAULT  | ProductName | Product name of the wallbox  |


## Usefull links
- https://github.com/victronenergy/dbus_modbustcp/blob/master/CCGX-Modbus-TCP-register-list.xlsx
- https://github.com/trixing/venus.dbus-twc3

## Discussions on the web
