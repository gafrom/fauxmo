# fauxmo
**Emulated Belkin WeMo devices that work with the Amazon Echo**

All of the code to make it work is contained in the single file, `fauxmo.py`. It
requires Python 2.7 and standard libraries.

## Usage

```python
devices = (
  Device('kitchen light', RelayHandler(17),    None, 10005),
  Device('garden gate',   GateHandler(23, 24), None, 10006)
)

server = UpnpServer(devices)
server.start()
```

Clone this repository, add your devices to `fauxmo.py` file and execute it. If you want debug output, execute `./fauxmo.py -d`. If you want it to run for an extended period, you could do something like `nohup ./fauxmo.py &`
or turn it into a systemd service and enable it (please refer to the section below).

Once fauxmo.py is running, simply tell _"Alexa, discover devices"_. You can
also do this from the Alexa App or web at alexa.amazon.com.

## Enable systemd service

Create a file `/lib/systemd/system/fauxmo.service` with the following contents:
```service
[Unit]
Description=Emulator of WeMo devices

[Service]
Type=simple
ExecStart=/usr/bin/fauxmo -d

[Install]
WantedBy=multi-user.target
```

## Make Raspberry connect to Wifi

After burning a Raspberry OS to the SD card, put a file `/Volume/boot/wpa_supplicant.conf` (to Raspberry SD card):
```conf
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="<name of your Wifi>"
    psk="<password of your Wifi>"
    key_mgmt=WPA-PSK
}
```
