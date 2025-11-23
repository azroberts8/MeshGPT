import time
import asyncio
from pubsub import pub

import meshtastic
import meshtastic.serial_interface
from ollama import chat, ChatResponse, Message


SYSTEM_PROMPT = "You are MeshGPT, a HAM enthusiast on the Meshtastic network located in Delaware. All responses should be less than 50 words."
chats: dict[int, list[Message]] = {}

def split_message(message: str) -> list[str]:
    """Splits message into list of strings where len(str) < 200 characters to fit mesh standard"""
    words = message.split()
    chunks = []
    current = []

    for word in words:
        # If adding this word would exceed the limit, start a new chunk
        if current and len(" ".join(current + [word])) > 192:  # 200 char limit; up to 8 seq chars _(xx/xx)
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        chunks.append(" ".join(current))

    return chunks


def on_receive(packet, interface):
    """Handles incoming mesh packets"""

    # Only process messages with 'decoded' section available
    decoded = packet.get("decoded")
    if not decoded:
        return

    # Ignore nodeinfo & telemetry - only text messages
    portnum = decoded.get("portnum")
    if portnum != "TEXT_MESSAGE_APP":
        return

    # Respond only when message is addressed directly to us (not main chat)
    recipient = packet.get("to")
    if recipient != my_node:
        return

    # Only response to messages where we know the sender
    sender = packet.get("from")
    if not sender:
        return

    text = decoded.get("payload", "")
    asyncio.run(respond(text, sender))  # run async so response generation does not block main thread


async def respond(received_message, sender):
    """Tracks device-specific conversations and generates responses with Ollama"""

    print(f"\nFrom: {sender}\nReceived: {received_message}")

    # If no conversation history exists with sender - start conversion with system prompt
    if sender not in chats:
        chats[sender] = [Message(
            role='system',
            content=SYSTEM_PROMPT
        )]

    # Add user message to appropriate chat & generate response
    chats[sender].append(Message(
        role='user',
        content=received_message
    ))
    response = chat(model='gemma3:1b', messages=chats[sender])

    # Send response to mesh device
    print(f"Responding: {response.message.content}")
    msg_chunks = split_message(response.message.content)
    for i in range(len(msg_chunks)):
        chunk = f"{msg_chunks[i]} ({i+1}/{len(msg_chunks)})" if len(msg_chunks) > 1 else msg_chunks[0]
        interface.sendText(chunk, destinationId=sender)
        time.sleep(2)

    # Add response to chat history
    chats[sender].append(Message(
        role='assistant',
        content=response.message.content
    ))


pub.subscribe(on_receive, "meshtastic.receive")

interface = meshtastic.serial_interface.SerialInterface()
my_node = interface.myInfo.my_node_num
print("Ready!")

while True:
    time.sleep(1)
