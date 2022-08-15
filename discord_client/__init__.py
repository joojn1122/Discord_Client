import websocket
import json
from threading import Thread
import time
import sys

import requests
from requests.models import Response

class DiscordGateWay:

	def __init__(self, client):
		self.client = client

	def send_json_request(self, request) -> None:
		self.ws.send(json.dumps(request))

	def recieve_json_response(self) -> dict:
		response = self.ws.recv()

		if response:
			return json.loads(response)

	def heartbeat(self, interval):

		while self.running:

			try:
				time.sleep(interval)

				heartbeatJSON = {
					"op" : 1,
					"d" : None
				}

				self.send_json_request(heartbeatJSON)

			except KeyboardInterrupt:
				self.stop()

	def start(self):
		self.ws = websocket.WebSocket()
		self.ws.connect("wss://gateway.discord.gg/?v=6&encoding=json")
		event = self.recieve_json_response()

		self.client.on_event(event)
		self.running = True

		interval = event['d']['heartbeat_interval'] / 1000
		Thread(target=self.heartbeat, args=[interval]).start()

		Thread(target=self.event_thread).start()

	def stop(self):
		self.running = False

	def event_thread(self):
		payload = {
			"op" : 2,
			"d" : {
				"token" : self.client.headers["authorization"],
				"properties" : {
					"$os" : "windows",
					"$browser" : "chrome",
					"$device" : "pc"
				}
			}
		}

		self.send_json_request(payload)

		while self.running:
			event = self.recieve_json_response()

			self.client.on_event(event)

class Client:

	def __init__(self, token):

		self.headers = {
			"authorization" : token
		}

		self.events = {}
		self.action = Action(self.headers)

	def start_gateway(self) -> None:
		self.gateway = DiscordGateWay(self)
		self.gateway.start()

	def hook_event(self, event: str, callback : callable) -> None:
		self.events[event] = callback

	def on_event(self, event: dict) -> None:

		if event == None: 
			return

		callback = self.events.get(event["t"], None)

		if callback is None: 
			return

		callback(event["d"])

class Action:

	BASE = "https://discord.com/api/v9"

	def __init__(self, headers):
		self.headers = headers

	def send_request(self, method, url, **kwargs) -> Response:

		return requests.request(method, f"{self.BASE}{url}", headers=self.headers, **kwargs)

	def send_chat_message(self, channel_id: str, message: str, *, reply_msg_id=None, tts=False) -> Response:
		payload = {
			"content" : message
		}

		if reply_msg_id is not None:
			payload["message_reference"] = {
				"channel_id" : channel_id,
				"message_id" : reply_msg_id
			}

		return self.send_request("POST", f"/channels/{channel_id}/messages", json=payload)

	def remove_chat_message(self, channel_id: str, message_id: str) -> Response:

		return self.send_request("DELETE", f"/channels/{channel_id}/messages/{message_id}")

	def get_user_info(self, user_id: str) -> Response:

		return self.send_request("GET", f"/users/{user_id}/profile")

	def send_typing_action(self, channel_id: str) -> Response:

		return self.send_request("GET", f"/channels/{channel_id}/typing")

	def send_friend_request(self, user_id: str) -> Response:

		return self.send_request("PUT", f"/users/@me/relationships/{user_id}", json={})

	def remove_friend_request(self, user_id: str) -> Response:

		return self.send_request("DELETE", f"/users/@me/relationships/{user_id}")

	def create_group(self, users: list) -> Response:

		return self.send_request("POST", "/users/@me/channels", json={
			"recipients" : users
			})

	def leave_group(self, channel_id: str) -> Response:

		return self.send_request("DELETE", f"/channels/{channel_id}")

	def kick_user(self, channel_id: str, user_id: str) -> Response:

		return self.send_request("DELETE", f"/channels/{channel_id}/recipients/{user_id}")

	def get_profile(self) -> dict:

		return self.send_request("GET", "/users/@me").json()
