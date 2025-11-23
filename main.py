import time
import asyncio
from pubsub import pub

import meshtastic
import meshtastic.serial_interface
from ollama import chat, ChatResponse, Message


SYSTEM_PROMPT = "You are MeshGPT, a helpful assistant that keeps messages short. All responses should be less than 50 words."
chats: dict[int, list[Message]] = {}


def on_receive(packet, interface):
    decoded = packet.get("decoded")
    if not decoded:
        return

    portnum = decoded.get("portnum")
    if portnum != "TEXT_MESSAGE_APP":
        return

    recipient = packet.get("to")
    if recipient != my_node:
        return

    sender = packet.get("from")
    if not sender:
        return

    text = decoded.get("payload", "")
    asyncio.run(respond(text, sender))


async def respond(received_message, sender):
    print(f"\nFrom: {sender}\nReceived: {received_message}")
    if sender not in chats:
        chats[sender] = [Message(
            role='system',
            content=SYSTEM_PROMPT
        )]
    chats[sender].append(Message(
        role='user',
        content=received_message
    ))
    response = chat(model='gemma3:1b', messages=chats[sender])
    interface.sendText(response.message.content, destinationId=sender)
    chats[sender].append(Message(
        role='assistant',
        content=response.message.content
    ))


pub.subscribe(on_receive, "meshtastic.receive")

interface = meshtastic.serial_interface.SerialInterface()
my_node = interface.myInfo.my_node_num
print("Ready!")

try:
    while True:
        time.sleep(1)
except Exception as e:
    print("Exiting...")
