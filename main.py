import time
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

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
    respond(text, sender)


def respond(received_message, sender):
    print(f"\nReceived: {received_message}")
    response = input("Response: ")
    interface.sendText(response, destinationId=sender)


pub.subscribe(on_receive, "meshtastic.receive")

interface = meshtastic.serial_interface.SerialInterface()
my_node = interface.myInfo.my_node_num
print("Ready!")

try:
    while True:
        time.sleep(1)
except Exception as e:
    print("Exiting...")
