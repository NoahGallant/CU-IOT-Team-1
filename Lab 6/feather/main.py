from machine import Pin as PIN

from machine import ADC

from machine import I2C

from machine import RTC

from network import WLAN, STA_IF

import ssd1306 as OLED

import time

import gesture

import weather

import url_request

import ntptime

import urequests





try:

	import usocket as socket

except:

	import socket



# press external button to show 

# press a button to add 1 hour

# press b button to add 1 minute

# press c button to add 10 sec

# press a + b buttons to enter "alarm setup" and again to exit

# press b + c buttons to enter "gesture mode" and again to exit

## while on "gesture mode":

## press a button to record a gesture and again to stop

## press c button to train a gesture and again to stop





ssid = 'Columbia University'

password = ''



alarm_length = 10

gest_samp_num = 20

loop_time = 0.1

buttons_delay = 0.1



a_pin = 14

b_pin = 12

c_pin = 13

# button_pin = 15

accel_addr = 83



# init time

dt = [2018, 10, 31, 0, 15, 0, 0, 0]



# init alarm

alarm_H = 15

alarm_M = 0

alarm_S = 20

alarm_setup = False



# init gesture

columbia = ["C", "O", "L", "U", "M", "B", "I", "A"]

# columbia = ["C", "O"]

gest_samps = {"X":[], "Y":[], "Z":[]}

letter = 0

gesture_mode = False

gesture_record = False

gesture_record_end = False

gesture_train = False

gesture_train_end = False

show_data = False



a_pressed = False

b_pressed = False

c_pressed = False





def wifi_connect(oled, ssid='', password=''):

	# init network

	sta_if = WLAN(STA_IF)

	sta_if.active(True)

	sta_if.connect(ssid, password)



	# wait for the feather to connect

	while not sta_if.isconnected():

		oled.text("Connecting to network...", 0, 0)

		oled.show()



	# print the IP address

	oled.fill(0)

	oled.text(sta_if.ifconfig()[0], 0, 0)

	print(sta_if.ifconfig()[0])

	oled.show()



	time.sleep(5.0)



	return sta_if



def get_xyz(accel_addr):



    accel_x0 = i2c.readfrom_mem(accel_addr, 0x32, 1)

    accel_x1 = i2c.readfrom_mem(accel_addr, 0x33, 1)

    accel_x = bin2dec(accel_x1, accel_x0)



    accel_y0 = i2c.readfrom_mem(accel_addr, 0x34, 1)

    accel_y1 = i2c.readfrom_mem(accel_addr, 0x35, 1)

    accel_y = bin2dec(accel_y1, accel_y0)



    accel_z0 = i2c.readfrom_mem(accel_addr, 0x36, 1)

    accel_z1 = i2c.readfrom_mem(accel_addr, 0x37, 1)

    accel_z = bin2dec(accel_z1, accel_z0)



    return accel_x, accel_y, accel_z





def bin2dec(msb, lsb):

	out = (msb[0] << 8) + lsb[0]

	if out & 0x8000 != 0:

		out = ~out + 1

		out = -1* (out + 65535)

	

	return out





def a_callback(p):

	a_button.irq(trigger=0, handler=a_callback)

	time.sleep(0.01)

	global a_pressed

	a_pressed = True



	time.sleep(buttons_delay)

	a_button.irq(trigger=PIN.IRQ_FALLING, handler=a_callback)





def b_callback(p):

	b_button.irq(trigger=0, handler=b_callback)

	time.sleep(0.01)

	global b_pressed

	b_pressed = True



	time.sleep(buttons_delay)

	b_button.irq(trigger=PIN.IRQ_FALLING, handler=b_callback)





def c_callback(p):

	c_button.irq(trigger=0, handler=c_callback)

	time.sleep(0.01)

	global c_pressed

	c_pressed = True



	time.sleep(buttons_delay)

	c_button.irq(trigger=PIN.IRQ_FALLING, handler=c_callback)



# def button_callback(p):

# 	external_button.irq(trigger=0, handler=button_callback)

# 	time.sleep(0.01)

# 	global button_pressed

# 	button_pressed = True



# 	time.sleep(buttons_delay)

# 	external_button.irq(trigger=PIN.IRQ_FALLING, handler=button_callback)





a_button = PIN(a_pin, PIN.IN, PIN.PULL_UP)

a_button.irq(trigger=PIN.IRQ_FALLING, handler=a_callback)



b_button = PIN(b_pin, PIN.IN, None)

b_button.irq(trigger=PIN.IRQ_FALLING, handler=b_callback)



c_button = PIN(c_pin, PIN.IN, PIN.PULL_UP)

c_button.irq(trigger=PIN.IRQ_FALLING, handler=c_callback)



# external_button = PIN(button_pin, PIN.IN, PIN.PULL_UP)

# external_button.irq(trigger=PIN.IRQ_FALLING, handler=button_callback)



pin_0 = PIN(0, PIN.OUT)

pin_0.on()



adc = ADC(0)



i2c = I2C(-1, PIN(5), PIN(4))

oled = OLED.SSD1306_I2C(128, 32, i2c)



oled.fill(1)

oled.show()

time.sleep(0.2)



i2c.writeto_mem(accel_addr, 0x2D, b'x08')


lastTweet = "No last Tweet"
lastWeather = "No last weather"


x_init, y_init, z_init = get_xyz(accel_addr)

# x_init, y_init, z_init = 0, 0, 0


alarmOn = False



display_on = True

clock_on = True



x_pos = 30

y_pos = 10

z_pos = 10



alarm_counter = alarm_length



sta_if = wifi_connect(oled, ssid, password)


# bind socket to port 8080

s_app = socket.socket()
ai = socket.getaddrinfo("0.0.0.0", 8080)
addr = ai[0][-1]
s_app.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s_app.bind(addr)
s_app.listen(5)
s_app.settimeout(0.5)

# s_aws = socket.socket()
# ai = socket.getaddrinfo("0.0.0.0", 9090)
# addr = ai[0][-1]
# s_aws.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# s_aws.bind(addr)
# s_aws.listen(5)
# s_aws.settimeout(0.5)

# weather.get(oled)
# 	url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyChG6K10u852YhlBESGv1VmyepIDycr2dg'
# 	headers = {'content-type': 'application/json'}
# 	print("before post")
# 	resp = urequests.post(url, data='{}', headers=headers)
# 	print("after post")
# 	d = resp.json()

# time.sleep(20.0)



# set up real-time-clock


try:
	ntptime.settime()
	r_time = RTC()
	dt = r_time.datetime()
	dt[4] -= 4
	time.datetime(dt)
except:
	r_time = RTC()
	r_time.datetime(dt)





while True:

	if gesture_mode == False and alarm_setup == False:

		try:

			# conn, conn_add = s_app.accept()

			# display_on, clock_on, lastTweet, lastWeather = url_request.get(s_app, display_on, clock_on, oled)

			res = s_app.accept()
			client_s = res[0]
			client_addr = res[1]
			print("after accept")
			req = client_s.recv(2048)
			print("after socket.receive")
			response, display_on, clock_on, lastTweet, lastWeather = url_request.get(req, display_on, clock_on, oled, lastTweet, lastWeather)
			print(int(display_on))

			client_s.send(response)
			client_s.close()

		except Exception as ex:
			print(ex)
			# clock_on = True



	# alarm setup

	if a_pressed and b_pressed and alarm_setup == False and gesture_mode == False:

		alarm_setup = True

	elif a_pressed and b_pressed and alarm_setup == True:

		alarm_setup = False

	# gesture mode

	elif b_pressed and c_pressed and gesture_mode == False and alarm_setup == False:

		gesture_mode = True

	elif b_pressed and c_pressed and gesture_mode == True:

		gesture_mode = False

		gesture_record = False

		gesture_train = False

		gest_samps["X"] = []

		gest_samps["Y"] = []

		gest_samps["Z"] = []



	# gesture recording

	elif a_pressed and not b_pressed and gesture_mode == True and gesture_record == False and gesture_train == False:

		gesture_record = True

		gesture_record_end = False

	elif a_pressed and not b_pressed and gesture_mode == True and gesture_record == True:

		gesture_record = False

		gesture_record_end = True



	# gesture training

	elif not b_pressed and c_pressed and gesture_mode == True and gesture_train == False and gesture_record == False:

		gesture_train = True

		gesture_train_end = False

	elif not b_pressed and c_pressed and gesture_mode == True and gesture_train == True:

		gesture_train = False

		gesture_train_end = True


	# showing data mode
	elif a_pressed and c_pressed and show_data == True:

		show_data = False

	elif a_pressed and c_pressed and gesture_mode == False and alarm_setup == False:

		show_data = True


	# showing time

	elif gesture_mode == False:

		if a_pressed and not b_pressed:

			if alarm_setup:

				alarm_H += 1

				if alarm_H > 23:

					alarm_H = 0

			else:

				dt = list(r_time.datetime())

				if dt[-4] < 23:

					dt[-4] += 1

				elif dt[-4] == 23:

					dt[-4] = 0

				r_time.datetime(dt)





		if b_pressed and not c_pressed and not a_pressed:

			if alarm_setup:

				alarm_M += 1

				if alarm_M > 59:

					alarm_M = 0

			else:

				dt = list(r_time.datetime())

				if dt[-3] < 59:

					dt[-3] += 1

				elif dt[-3] == 59:

					dt[-3] = 0

				r_time.datetime(dt)

		

		if c_pressed and not b_pressed:

			if alarm_setup:

				alarm_S += 10

				if alarm_S > 59:

					alarm_S = 0

			else:

				dt = list(r_time.datetime())

				if dt[-2] < 59:

					dt[-2] += 10

				elif dt[-2] == 59:

					dt[-2] = 0

				r_time.datetime(dt)



	a_pressed = False

	b_pressed = False

	c_pressed = False

	button_pressed = False



	# Alarm

	dt = r_time.datetime()

	time_H, time_M, time_S = dt[-4], dt[-3], dt[-2]

	if alarm_H == time_H and alarm_M == time_M and alarm_S == time_S:

		alarmOn = True

		pin_0.off()

	elif alarmOn == True and alarm_counter < 1:

		pin_0.on()

		alarmOn = False

		alarm_counter = alarm_length

	elif alarmOn == True:

		alarm_counter -= 1





	x, y, z = get_xyz(accel_addr)

	x_move = -1 * (x_init - x)

	y_move = y_init - y

	z_move = z_init - z



	if (x_move > 10 or x_move < -10):

		x_pos += (x_move//10)

	if (y_move > 10 or y_move < -10):

		y_pos += (y_move//10)



	if (x_move > 10 or x_move < -10):

		 x_pos += (x_move//10)

	if (y_move > 10 or y_move < -10):

		y_pos += (y_move//10)



	

	if alarm_setup:

		oled.fill(0)

		oled.text("%02d:%02d:%02d" % (alarm_H, alarm_M, alarm_S), 0, 0)

		oled.text("Alarm Setup", 20, 20)

	

	elif gesture_mode:

		oled.fill(0)

		if gesture_record:

			gesture.oled(oled, gest_samps, x_move, y_move, z_move, rec=1, train=0)

			gesture.get_and_send(gest_samps, x_move, y_move, z_move, rec=1, samp_num=gest_samp_num)

		elif gesture_record_end:

			gesture.oled(oled, gest_samps, x_move, y_move, z_move, rec=0, train=0)

			gesture.get_and_send(gest_samps, x_move, y_move, z_move, rec=0, samp_num=gest_samp_num)

			letter_pred = gesture.get_pred(oled)

			gesture_record_end = False

		

		elif gesture_train:

			gesture.oled(oled, gest_samps, x_move, y_move, z_move, rec=1, train=1, letter=columbia[letter])

			gesture.get_and_send(gest_samps, x_move, y_move, z_move, rec=1, letter=columbia[letter], samp_num=gest_samp_num)

		elif gesture_train_end:

			gesture.oled(oled, gest_samps, x_move, y_move, z_move, rec=0, train=1, letter=columbia[letter])

			res = gesture.get_and_send(gest_samps, x_move, y_move, z_move, rec=0, letter=columbia[letter], samp_num=gest_samp_num)

			if res == 1:

				letter += 1

			if letter == len(columbia):

				letter = 0

			gesture_train_end = False

		

		else:

			gesture.oled(oled, gest_samps, x_move, y_move, z_move, rec=0, train=0)

	elif show_data:

		oled.fill(0)

		oled.text(lastTweet, 0, 10)
		oled.text(lastWeather, 0, 20)


	elif clock_on:

		oled.fill(0)

		x_pos = int(x_pos % 120)

		y_pos = int(y_pos % 30)



		dt = r_time.datetime()

		dt = str(dt[-4])+":"+str(dt[-3])+":"+str(dt[-2])

		oled.text(dt, x_pos, y_pos)		



	read = adc.read()

	oled.contrast(read)


	if display_on == False:
		oled.fill(0)

	oled.show()

	#send response


	time.sleep(loop_time)

