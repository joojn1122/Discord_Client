from discord_client import Client

#from karelbot import get_response
from ai import get_response

from word_football import get_random_word


with open("token.txt", "r") as f:
	token = f.read()

client = Client(token)
client.start_gateway()

def on_message(event):
	username = event["author"]["username"]
	disc = event["author"]["discriminator"]
	channel_id = event["channel_id"]

	# if == return

	message = event["content"]

	if "<" in message and ">" in message: return

	print(f"{username} said {message}")

	client.send_typing_action(channel_id)

	if channel_id == "1007582760380137614":
		response = get_random_word(message[::-1][0])

		if response == None:
			return

		time.sleep(len(response) / 5)

	else:
		# sleep implemented in get_response
		response = get_response(message)

	client.send_chat_message(channel_id, response, reply_msg_id=(event["id"] if random.randint(0, 1) == 0 else None))


client.hook_event("MESSAGE_CREATE", on_message)