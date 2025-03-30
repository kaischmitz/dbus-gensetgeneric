# dbus-gensetgeneric
Integrate any genset into Victron Energies Venus OS

## Purpose
With the scripts in this repo it should be easily possible to install, uninstall, restart a service that sets up the DBUS structure for any genset in VenusOS and GX devices from Victron.
The idea is to fill this structure later on via MQTT. The genset then shows up in Venus OS and VRM.
Forked from dbus-goecharger by vikt0rm.


## How it works
### Why? ###
I have a generator with a homemade controller and I want to supply the status of the generator to VRM.

### Details / Process
What is the script doing:
- Running as a service
- connecting to DBus of the Venus OS `com.victronenergy.genset.generic_{DeviceInstanceID_from_config}`
- Paths are added to the DBus with default value 0 - including some settings like name, etc
- After that a "loop" is started which can handle updated values by callback - nothing in there yet
- After successful DBus connection all data points need to be updated via MQTT. The coding of the data points is listed in [CCGX-Modbus-TCP-register-list.xlsx](https://github.com/victronenergy/dbus_modbustcp/blob/master/CCGX-Modbus-TCP-register-list.xlsx) in the field list under com.victronenergy.genset
- The DBUS data point /Start can be used for generator start/ stop. Alternatively you can select "connected genset helper relay" in the settings for Relay 1 and use the built in Relay for start/ stop

## Install & Configuration
### Get the code
Just grap a copy of the main branch and copy them to a folder under `/data/` e.g. `/data/dbus-gensetgeneric`.
After that call the install.sh script.

The following script should do everything for you:
```
wget https://github.com/kaischmitz/dbus-gensetgeneric/archive/refs/heads/main.zip
unzip main.zip "dbus-gensetgeneric-main/*" -d /data
mv /data/dbus-gensetgeneric-main /data/dbus-gensetgeneric
chmod a+x /data/dbus-gensetgeneric/install.sh
/data/dbus-gensetgeneric/install.sh
rm main.zip
```
⚠️ Check configuration after that - because service is already installed an running and with wrong connection data (host) you will spam the log-file

### Change config.ini
Within the project there is a file `/data/dbus-gensetgeneric/config.ini` - just change the values - most important is the deviceinstance under "DEFAULT". More details below:

| Section  | Config vlaue | Explanation |
| ------------- | ------------- | ------------- |
| DEFAULT  | SignOfLifeLog  | Time in minutes how often a status is added to the log-file `current.log` with log-level INFO |
| DEFAULT  | Deviceinstance | Unique ID identifying the genset in Venus OS |
| DEFAULT  | CustomName | Custom name of the genset  |
| DEFAULT  | ProductName | Product name of the genset  |


## Usefull links
- https://github.com/victronenergy/dbus_modbustcp/blob/master/CCGX-Modbus-TCP-register-list.xlsx
- https://github.com/victronenergy/venus/wiki/dbus#generator-data
