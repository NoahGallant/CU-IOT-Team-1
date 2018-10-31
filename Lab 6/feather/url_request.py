import weather
import urequests

twitter_url = "http://maker.ifttt.com/trigger/IOT_test/with/key/cqDlfrSdRyyvFlboVcEB_Z"

def get(req, display_on, clock_on, oled, twitter, weather_str):
	
	# grab the endpoint/command
	print("executed get")
	results = str(req).split("/")
	c = results[1].split(" ")[0].replace("%20", " ")
	if c == "favicon.ico":
		print('No command...')
		return display_on, clock_on
	command = c
	print(command)

	# general wrapper for HTTP/1.0 communication
	CONTENT = b"""\
HTTP/1.0 200 OK \r\n
%s!
"""
	if (len(command) > 5):
		begin = command[0:5] 
	
	# handle the command
	if (command == "turn on the display"):
		display_on = True
		response = CONTENT % 'Display turned on!'
	elif (command == "turn off the display"):
		display_on = False
		response = CONTENT % 'Display turned off!'
	elif (command == "display the time"):
		clock_on = True
		response = CONTENT % 'Switched to watch mode!'
	elif (begin == 'tweet'):
		clock_on = False
		if (len(command) > 6):
			twitString = command[6:len(command)]
			response = CONTENT % (twitString + ' has been tweeted')
			oled.fill(0)
			oled.text('tweeted: ', 0, 10)
			oled.text(twitString, 0, 20)
			twitString = twitString.replace(' ', '+')
			urlData = twitter_url + '?value1=' + twitString
			urequests.get(urlData)
			twitter = twitString
		else:
			oled.text('nothing to tweet')
			response = CONTENT % 'nothing to tweet'
		oled.show()

	elif (command == 'display the weather'):
		clock_on = False
		weatherS, tempS = weather.get(oled)
		oled.fill(0)
		oled.text(weatherS,0,10)
		oled.text(tempS,0,20)
		oled.show()
		response = CONTENT % (weatherS + tempS)
		weather_str = weatherS

	else:
		# clock_on = False
		# oled.fill(0)
		# oled.text(command, 0, 0)
		# oled.show()
		response = CONTENT % 'Message displayed on watch!'
	print("got here!")

	print(response, display_on, clock_on)
	return response, display_on, clock_on, twitter, weather_str