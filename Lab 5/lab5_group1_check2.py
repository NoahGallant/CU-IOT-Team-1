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

# connect to internet
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Columbia University')

# setup OLED
i2c = I2C(-1, PIN(5), PIN(4))
oled = OLED.SSD1306_I2C(128, 32, i2c)

# wait for connection
while not sta_if.isconnected():
    oled.text("Connecting to network...", 0, 0)
    oled.show()

# print IP
oled.fill(0)
oled.text(sta_if.ifconfig()[0], 0, 0)
oled.show()

#attach socket to port
s = socket.socket()
ai = socket.getaddrinfo("0.0.0.0", 8080)
addr = ai[0][-1]
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)

CONTENT = b"""\
HTTP/1.0 200 OK \r\n
Request to watch received!
"""

# continually handle connections
while True:
    res = s.accept()
    client_s = res[0]
    client_addr = res[1]
    req = client_s.recv(4096)

    client_s.send(CONTENT)
    client_s.close()

    