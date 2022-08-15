from discord_client import Client
import random

client = Client("<YOUR TOKEN">)
client.start_gateway() # connect to discord server to reveive events (without this events won't work)

profile = client.action.get_profile()

def on_message(event):
	username = event["author"]["username"]
	disc = event["author"]["discriminator"]
	channel_id = event["channel_id"]
	message = event["content"]

	# filter your messages
	if username == profile["username"] and disc == "your disc":
		return
	
	print(f"{username} said {message}")
	
	# send typing action
	client.send_typing_action(channel_id)
	
	# send welcome message and there's 50% change to reply to the user's message or send it normally
	client.send_chat_message(channel_id, f"Hello {username}!", reply_msg_id=(event["id"] if random.randint(0, 1) == 0 else None))


client.hook_event("MESSAGE_CREATE", on_message)
