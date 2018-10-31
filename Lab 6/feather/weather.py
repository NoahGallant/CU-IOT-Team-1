import urequests
import time

def get(oled, d):
	url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyChG6K10u852YhlBESGv1VmyepIDycr2dg'
	headers = {'content-type': 'application/json'}
	print("before post")
	resp = urequests.post(url, data='{}', headers=headers)
	print("after post")
	d = resp.json()

	if 'location' in d:
		latitude = d['location']['latitidue']
		longitude = d['location']['longitude']
	else: #we reached our API limit
		oled.fill(0)
		oled.text("Reached Google location API limit", 0, 0)
		oled.show()
		time.sleep(2.0)
		return

	oled.fill(0)
	oled.text("%02d, %02d" % (latitude, longitude), 0, 0)
	oled.text("Loading weather...", 0, 10)
	oled.show()

	geocode_url = "https://api.openweathermap.org/data/2.5/weather?lat="+str(latitude)+"&lon="+str(longitude)+"&appid=2cf524df462ded789b9600c8611e2a74"
	results = urequests.get(geocode_url)
	results = results.json()

	weather = None
	temp = None
	if 'weather' in results:
		weather = results['weather'][0]['description']
	if 'main' in results:
		temp = results['main']['temp']

	if weather is not None and temp is not None:
		return weather + "Temp = " + str(temp)+"K"
	elif weather is not None and temp is None:
		return weather + "No Temp Records"
	elif weather is None and temp is not None:
		return"No Weather Records, Temp = " + str(temp)+"K"
	else:
		return "No Weather or Temp Records"
