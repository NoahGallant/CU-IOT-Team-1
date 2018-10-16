import network
import machine

try:
    import usocket as socket
except:
    import socket

from machine import I2C
import ssd1306 as OLED
import time

from machine import Pin as PIN


###########
###########
## LAB 5 ##
###########
###########


sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

sta_if.connect('Columbia University')

i2c = I2C(-1, PIN(5), PIN(4))
oled = OLED.SSD1306_I2C(128, 32, i2c)


# wait for the feather to connect
while not sta_if.isconnected():
    oled.text("Connecting to network...", 0, 0)
    oled.show()


# set up real-time-clock
rtc = machine.RTC()
rtc.datetime((2018, 10, 17, 0, 4, 13, 0, 0))

# print the IP address
oled.fill(0)
oled.text(sta_if.ifconfig()[0], 0, 0)
oled.show()

################
# Checkpoint 3 #
################

# bind socket to port 8080
s = socket.socket()
ai = socket.getaddrinfo("0.0.0.0", 8080)
addr = ai[0][-1]
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)
s.settimeout(1.0)

# general wrapper for HTTP/1.0 communication
CONTENT = b"""\
HTTP/1.0 200 OK \r\n
%s!
"""

# global vars
clock_on = True
display_on = True
text = sta_if.ifconfig()[0]

while True:
    # try for one second, timeout so we can update clock
    text = sta_if.ifconfig()[0]
    try:
        res = s.accept()
    except:
        if(clock_on and display_on):
            dt = rtc.datetime()
            text = str(dt[-4])+":"+str(dt[-3])+":"+str(dt[-2])
            oled.fill(0)
            oled.text(text,0,0)
            oled.show()
        continue

    client_s = res[0]
    client_addr = res[1]
    req = client_s.recv(4096)

    # grab the endpoint/command
    results = str(req).split("/")
    c = results[1].split(" ")[0].replace("%20", " ")
    if c == "favicon.ico":
        continue
    command = c

    # handle the command
    if (command == "turn on display"):
        display_on = True
        response = CONTENT % 'Display turned on!'
    elif (command == "turn off display"):
        display_on = False
        response = CONTENT % 'Display turned off!'
    elif (command == "show the time"):
        clock_on = True
        response = CONTENT % 'Switched to watch mode!'
    else:
        text = command
        clock_on = False
        response = CONTENT % 'Message displayed on watch!'

    # update screen
    if clock_on:
        dt = rtc.datetime()
        text = str(dt[-4])+":"+str(dt[-3])+":"+str(dt[-2])
    
    if display_on:
        oled.fill(0)
        oled.text(text, 0, 0)
        oled.show()
    else:
        oled.fill(0)
        oled.show()

    #send response
    client_s.send(response)
    client_s.close()
    