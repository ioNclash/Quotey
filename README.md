# Quotey
A low power device to display impactful messages daily. 
Upload a set of quotes to the device and see it change to display a new quote each day!
Dynamically add new quotes by interfacing with a preloaded API

## Table of Contents
- [Implementation](#implementation)
- [Setup Instructions](#setup-instructions)
  - [Parts I Used](#parts-i-used)
  - [Setting up the Pi OS](#setting-up-the-pi-os)
  - [Cloning the repository](#cloning-the-repository)
  - [The Startup Script](#the-startup-script)
  - [The API](#the-api)
    - [Home Assistant Integration](#home-assistant-integration) 
- [Credits](#credits)
## Implementation
This project was written in python, using PIL for text display, waveshare epd libraries to interface with the screen and python flask with gunicorn to host the api, alowing remote easy upload of quotes to the device. This repository includes a bash script in order to setup the brunt of the scripts and file system scaffolding
## Setup Instructions
The setup of this project is relatively easy and requires only a little technical knowledge (mainly for ssh and interfacing with the API), i have divided this instruction set into easy to digest sections
### Parts I Used
To assemble this device all you will need is:
  - [**Raspberry pi Zero 2w**](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
    - GPIO Headers (Alternatively if you don't want to solder get a Pi zero 2w with these pre-installed) 
    - Micro usb power supply
    - SD card (32GB is more than enough)
  - [**Waveshare E ink display hat 2.13 in**](https://www.waveshare.com/2.13inch-e-Paper-HAT.htm)
  - OPTIONAl **Case** (you can find some good cases that incorporate both the pi and the screen online, or 3D print your own)
### Setting up the Pi OS
To setup the PI OS:

1. **Download / Run Pi Imager**.
2. **Select Raspberry Pi Model**: Choose **Raspberry Pi Zero 2 W**.
3. **Select OS**: Choose **Raspbian 64 Bit Lite**.
4. **Configure SSH Settings**: Enable SSH and set your SSH key for accessing the Pi remotely.
5. **Etch the OS onto the SD Card**: Write the OS to your SD card, then insert it into the Raspberry Pi and plug in the power.
6. **SSH into Raspberry Pi**: Connect remotely. At this point, it may be beneficial to give the Pi a static IP address.
7. **Open Terminal and Run the Following Command**:
    ```bash
    sudo raspi-config
    ```
    - Choose **Interfacing Options**.
    - Select **SPI**.
    - Choose **Yes** to enable the SPI interface.
8. **Reboot the pi using the following command**:
   ```bash
    sudo reboot
    ```
### Cloning the Repository
The OS does not come with git preinstalled so first run
```bash
  sudo apt install git
```
Then clone:
```bash
  git clone https://https://github.com/ioNclash/Quotey
```
Once this is done, cd into the repository to continue with the next steps:
```bash
  cd /path/to/quotey
```
### The Startup Script
The startup script automatically runs a lot of privalleged commands, if you are worried about this, feel free to inspect the script before running. When you're happy run:
```bash
chmod +x setup.sh
sudo ./setup.sh
```
After this has been ran, you will have all the needed libraries and json files, the quote change script will be set to display at midnight and the API will be running
### The API
The API has 5 uses:
/ GET - Returns help on how to use the api
/quote GET - Returns the daily quote as quote:{quotation:"str",source:"str",author:"str"}
/quote POST - Adds a new quote, payload should have string fields quotation, source and author
/quotes GET - Returns an array of quote objects
/quotes POST - Replaces the contents of quote.json with the payload. payload should be in the format quotes: with an array of quote objects

You can integrate the API with any platform you see fit, or use curl or postman if you feel like avoiding the hastle
#### Home Assistant Integration
To use the API, i built a home assistant integration to show me the daily quote on my dashboard and add quotes through a series of input boxes
<img width="583" height="571" alt="image" src="https://github.com/user-attachments/assets/ba399d06-25f5-41d3-9725-b513a1ac09bb" />

**Configuration.yaml**
```yaml
REST sensor to show current quote
sensor:
  - platform: rest
    name: Current Quote
    unique_id: current_quote_sensor
    resource: http://IP ADDR:5000/quote
    method: GET
    headers:
      Content-Type: application/json
    value_template: "{{ value_json.quote.quotation }}"
    json_attributes_path: "$.quote"
    json_attributes:
      - quotation
      - author
      - source
    scan_interval: 3600

# Input helpers for quote form
input_text:
  quote_quotation:
    name: Quote Text
    max: 255
  quote_author:
    name: Quote Author
    max: 100
  quote_source:
    name: Quote Source
    max: 100


# REST command to post quote    
rest_command:
  add_quote:
    url: "http://IP ADDR/quote"
    method: POST
    headers:
      Content-Type: application/json
    payload: >
      {
        "quotation": "{{ quotation }}",
        "author": "{{ author }}",
        "source": "{{ source }}"
      }
```
**scripts.yaml**
```yaml
add_quote:
  alias: Add Quote
  fields:
    quotation:
      description: The quote text
    author:
      description: The author of the quote
    source:
      description: The source of the quote
  sequence:
    - service: rest_command.add_quote
      data:
        quotation: "{{ quotation }}"
        author: "{{ author }}"
        source: "{{ source }}"
    - service: input_text.set_value
      target:
        entity_id:
          - input_text.quote_quotation
          - input_text.quote_author
          - input_text.quote_source
      data:
        value: ""
```
**Quote of the day card**
```markdown
type: markdown
title: Quote of the Day
content: >
  {{ state_attr('sensor.current_quote', 'quotation') }} — *{{
  state_attr('sensor.current_quote', 'author') }}*   ({{
  state_attr('sensor.current_quote', 'source') }})

```
**Add new Quote card**
```markdown
type: entities
title: Add New Quote
entities:
  - entity: input_text.quote_quotation
    name: Quotation
  - entity: input_text.quote_author
    name: Author
  - entity: input_text.quote_source
    name: Source
  - type: button
    name: Submit Quote
    action_name: Submit
    tap_action:
      action: call-service
      service: script.add_quote
      data:
        quotation: "{{ states('input_text.quote_quotation') }}"
        author: "{{ states('input_text.quote_author') }}"
        source: "{{ states('input_text.quote_source') }}"
    icon: mdi:send

```
## Credits
This project relies on a Waveshare EPD python module to interface with the E ink display

