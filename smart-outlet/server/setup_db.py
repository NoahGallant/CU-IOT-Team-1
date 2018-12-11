import pymongo
import datetime
import pprint

client = pymongo.MongoClient()
db = client.iot_4


user_1 = {"user_code": "noah", 
          "card_id": '123',
          "power": 2.0}

user_2 = {"user_code": "def", 
          "card_id": '345',
          "power": 1000.0}

db.users.insert_one(user_1)
db.users.insert_one(user_2)


points = db.points

point_1 = { "point_code": "123",
            "state": "ready",
            "user_code": "",
            "session": {
                'average_points': [0,0,0,0,0],
                "start_time": datetime.datetime.utcnow(),
                'power_used': 0
                }
            }

db.points.insert_one(point_1)
