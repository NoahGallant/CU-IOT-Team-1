import urequests
import time

global prediction
prediction = ""

def oled(oled, gest_samps, x_move, y_move, z_move, rec=1, train=0, letter=""):
	x_loc = 55
	if rec and not train:
		oled.text("X:"+str(x_move), 0, 0)
		oled.text("Y:"+str(y_move), 0, 10)
		oled.text("Z:"+str(z_move), 0, 20)
		oled.text("Gesture", x_loc, 0)
		oled.text("Rec", x_loc, 10)
		oled.text("Count:"+str(len(gest_samps["X"])) , x_loc, 20)
	elif not rec and not train:
		oled.text("X:"+str(x_move), 0, 0)
		oled.text("Y:"+str(y_move), 0, 10)
		oled.text("Z:"+str(z_move), 0, 20)
		oled.text("Gesture", x_loc, 0)
		oled.text("Mode", x_loc, 10)
		oled.text("Count:"+str(len(gest_samps["X"])) , x_loc, 20)
	elif rec and train:
		oled.text("X:"+str(x_move), 0, 0)
		oled.text("Y:"+str(y_move), 0, 10)
		oled.text("Z:"+str(z_move), 0, 20)
		oled.text("Gesture", x_loc, 0)
		oled.text("Train: "+letter, x_loc, 10)
		oled.text("Count:"+str(len(gest_samps["X"])), x_loc, 20)
		
	elif not rec and train:
		oled.text("X:"+str(x_move), 0, 0)
		oled.text("Y:"+str(y_move), 0, 10)
		oled.text("Z:"+str(z_move), 0, 20)
		oled.text("Gesture", x_loc, 0)
		oled.text("Train ended: "+letter, x_loc, 10)
		oled.text("Count:"+str(len(gest_samps["X"])), x_loc, 20)


def get_and_send(gest_samps, x, y, z, rec=0, letter="", samp_num=20):
	if rec:
		gest_samps["X"].append(x)
		gest_samps["Y"].append(y)
		gest_samps["Z"].append(z)
	else:
		rec_samp_len = len(gest_samps["X"])
		if rec_samp_len < 8:
			gest_samps["X"] = []
			gest_samps["Y"] = []
			gest_samps["Z"] = []
			return 0

		skip_samps = int(rec_samp_len / samp_num)
		if skip_samps > 1:
			gest_samps["X"] = gest_samps["X"][0::skip_samps]
			gest_samps["Y"] = gest_samps["Y"][0::skip_samps]
			gest_samps["Z"] = gest_samps["Z"][0::skip_samps]

		rec_samp_len = len(gest_samps["X"])
		if rec_samp_len > samp_num:
			gest_samps["X"] = gest_samps["X"][:samp_num]
			gest_samps["Y"] = gest_samps["Y"][:samp_num]
			gest_samps["Z"] = gest_samps["Z"][:samp_num]

		elif rec_samp_len < samp_num:
			num = samp_num - rec_samp_len
			gest_samps["X"] += [gest_samps["X"][-1]] * num
			gest_samps["Y"] += [gest_samps["Y"][-1]] * num
			gest_samps["Z"] += [gest_samps["Z"][-1]] * num

		data = [gest_samps["X"],gest_samps["Z"],gest_samps["Z"]]
		print(len(gest_samps["X"]), len(gest_samps["Y"]), len(gest_samps["Z"]))
		fulldata = {'letter':letter, 'data':data}
		try:
			r = urequests.post('http://100.24.14.22/insert', json = fulldata)
			print(r.status_code)
			global prediction
			prediction = r.text
		except:
			print("Server Error")

		

		gest_samps["X"] = []
		gest_samps["Y"] = []
		gest_samps["Z"] = []

		return 1


def get_pred(oled):

	oled.fill(0)
	oled.text(prediction, 10, 10)
	oled.show()
	time.sleep(2.0)

	return prediction

