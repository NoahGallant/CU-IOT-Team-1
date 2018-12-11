#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pymongo
import datetime
import pprint
from urllib.parse import urlparse, parse_qs

client = pymongo.MongoClient()
db = client.iot_4

users = db.users
points = db.points


def e(json_array):
    return str.encode(json.dumps(json_array))

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        print("here3")
        parts = self.path.split('?')
        query_components = parse_qs(urlparse(self.path).query)
        package = {'error': 'bad request'}
        point_code = '123'
        point = points.find_one({'point_code': point_code})
        if point and point['state'] == 'ready':
            point['session']['average_points'] = []
            point['session']['start_time'] = datetime.datetime.utcnow()
            point['session']['power_used'] = 0
        print("here4")
        if len(parts) > 1:
            user_and_card = 'user_code' in query_components and 'card_id' in query_components
            if parts[0] == '/info':
                if user_and_card:
                    user_code = query_components['user_code'][0]
                    package = user_info(user_code, query_components['card_id'][0])
                else:
                    package = {'error': 'parameters not filled'}
            elif parts[0] == '/relay':
                if user_and_card:
                    user_code = query_components['user_code'][0]
                    state = query_components['state'][0]
                    package = user_handshake(user_code, '123', state)
                else:
                    return {'error': 'parameters not filled'}
            elif parts[0] == '/point':
                if 'card_id' in query_components:
                    package = point_handshake(query_components['card_id'][0], '123')
                else:
                    return {'error': 'parameters not filled'}
            elif parts[0] == '/credit':
                if 'user_code' in query_components and 'credits' in query_components:
                    package = credit_user(query_components['user_code'][0], query_components['credits'][0])
            elif parts[0] == '/use':
                if 'usage' in query_components and 'signal' in query_components:
                    package = point_update('123', query_components['usage'][0], query_components['signal'][0])
                else:
                    package = {'error': 'parameters not filled'}
        pprint.pprint(package)
        self._set_headers()
        self.wfile.write(e(package))

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(b"<html><body><h1>POST!</h1></body></html>")
        

def credit_user(user_code, cred):
    user = users.find_one({'user_code': user_code})
    if not user:
        return {'error': 'user not found'}
    user['power'] = float(cred)
    users.save(user)
    return {'status': 'success'}


def user_info(user_code, card_id):
    user = users.find_one({'user_code': user_code})
    if not user:
        return {'error': 'user not found'}
    user['card_id'] = card_id
    users.save(user)
    if user:
        package = {
            'power_left': round(user['power'], 4),
            "user_code":  user_code,
            "server_message": "success",
        }
        point = points.find_one({'user_code': user_code})
        if point:
            seconds = (datetime.datetime.utcnow() - point['session']['start_time']).seconds
            if point['state'] == 'on':
                package["relay_state"] = point['state']
                package["time_used"] = str(int(seconds / 3600)) + ":" + str( int(seconds % 3600 / 60 )) + ":" + str(seconds % 60)
            elif point['state'] == 'user_confirm':
                package['relay_state'] = 'waiting for tap'
                package["time_used"] = ''
            else:
                package['relay_state'] = 'ready'
                package["time_used"] = ''
        else:
            package['relay_state'] = 'ready'
            package['time_used'] = ''
        return package
    return {'error': 'no user'}

def user_handshake(user_code, point_code, state):
    user = users.find_one({'user_code': user_code})
    point = points.find_one({'point_code': point_code})
    if user and point:
        if state == 'on':
            if (user['power'] > 0):
                point['user_code'] = user_code
                if point['state'] == 'ready' and state == 'on':
                    point['state'] = 'user_confirm'
                elif point['user_code'] == user_code and state == 'off':
                    point['state'] = 'ready'
                point['session']['power_used'] = 0
                points.save(point)
                return {
                    "power_left": round(user['power'], 4),
                    "user_code":  user_code,
                    "server_message": "success",
                    "relay_state": 'waiting for tap' if point['state'] == 'user_confirm' else 'ready',
                    "time_used": '',
                    "power_used": 0
                }
            else:
                return {'error': 'not enough power'}
        else:
            if (user_code == point['user_code']):
                point['state'] = 'ready'
                points.save(point)
                return {
                    "power_left": round(user['power'], 4),
                    "user_code":  user['user_code'],
                    "server_message": "success",
                    "relay_state": 'ready',
                    "time_used": '',
                    "power_used": 0
                }
            else:
                return {'error': 'point not available to this user'}
            
    else:
        return {'error': 'invalid code'}

def point_handshake(card_id, point_code):
    print('here0')
    user = users.find_one({'card_id': card_id})
    point = points.find_one({'point_code': point_code})
    print('here1')
    if user and point:
        if point['state'] == 'user_confirm' and point['user_code'] == user['user_code']:
            if (user['power'] > 0):
                point['state'] = 'on'
                point['session']['start_power'] = user['power']
                point['session']['start_time'] = datetime.datetime.utcnow()
                points.save(point)
                return {
                    "power_left":  round(user['power'], 4),
                    "user_code":  user['user_code'],
                    "server_message": "success",
                    "relay_state": 'on',
                    "time_used": '',
                    "power_used": 0
                }
            else:
                return {'error': 'not enough power'}
        else:
            return {'error': 'user not confirmed or relay already active'}
    return {'error': 'invalid code'}

def point_update(point_code, usage, signal):
    point = points.find_one({'point_code': point_code})
    print(float(usage))
    if signal == 'off':
        point['state'] = 'ready'
        points.save(point)
        return {'state': 'ready'}
    if point['state'] != 'on':
        return {'state': point['state']}
    else:
        user = users.find_one({'user_code': point['user_code']})
        user['power'] -= round(float(usage), 3)
        average_points = point['session']['average_points']
        if len(average_points) > 4:
            average_points.pop(0)
        average_points.append(float(usage))
        point['session']['average_points'] = average_points
        average = sum(average_points) / float(len(average_points))
        if average == 0:
            time_remaining = 0
        else:
            time_remaining = int(user['power'] / average)
        if user['power'] <= 0:
            user['power'] = 0
            point['state'] = 'ready'
            points.save(point)
            users.save(user)
            return {'state': 'ready'}
        users.save(user)
        points.save(point)
        return {'remaining':  round(user['power'], 4), 'time_remaining':  time_remaining}

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
