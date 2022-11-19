# Simple server for Raspberry Pi with Pimoroni Unicorn hat [HomeKit Edition]
This is based on the work of Elio (https://github.com/estruyf/unicorn-busy-server), but I added the support for HomeKit, via Homebridge (https://github.com/homebridge/homebridge) and the plugin homebridge-better-http-rgb (https://github.com/jnovack/homebridge-better-http-rgb).

# Light Bulb
Set the color like a RGB light bulb.<br>
![246FC6E2-A274-4134-8B30-D4A27643F847 2-2](https://user-images.githubusercontent.com/8201551/202852421-0e28d034-1939-4647-b683-f5b60b72a316.gif)<br><br>
Homebridge configuration (use your Homebridge <IP> and <PORT>):
```bash
        {
            "accessory": "HTTP-RGB",
            "name": "Hasellicht",
            "service": "Light",
            "switch": {
                "status": "<IP>:<PORT>/api/hb-status/switch",
                "powerOn": "<IP>:<PORT>/api/on",
                "powerOff": "<IP>:<PORT>/api/off"
            },
            "brightness": {
                "status": "<IP>:<PORT>/api/hb-status/brightness",
                "url": "<IP>:<PORT>/api/setb/%s"
            },
            "color": {
                "status": "<IP>:<PORT>/api/hb-status/color",
                "url": "<IP>:<PORT>/api/set/%s",
                "brightness": false
            }
        }
```

# Rainbow
Activate the rainbow like a switch:<br>
![246FC6E2-A274-4134-8B30-D4A27643F847-2](https://user-images.githubusercontent.com/8201551/202852430-8e7fd7a4-6260-44ab-b14f-5487c16bcfd9.gif)<br><br>
Homebridge configuration (use your Homebridge <IP> and <PORT>):
```bash
        {
            "accessory": "HTTP-RGB",
            "name": "Regenbogen",
            "service": "Light",
            "switch": {
                "status": "<IP>:<PORT>/api/hb-status/rainbow",
                "powerOn": "<IP>:<PORT>/api/rainbow",
                "powerOff": "<IP>:<PORT>/api/off"
            }
        }
```

# License

**MIT License**

Copyright (c) 2022 [*Justus*](https://github.com/justspacedog/)
Parts (c) 2020 [*Elio Struyf*](https://github.com/estruyf), [*Jamie Maynard*](https://github.com/j-maynard)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
