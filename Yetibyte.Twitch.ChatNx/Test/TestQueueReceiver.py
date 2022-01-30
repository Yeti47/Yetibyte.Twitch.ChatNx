from ChatNx.Irc import *
from ChatNx.QueueReceiver import *
from ChatNx.QueueReceiver.ChatNxQueueReceiverClient import *
from ChatNx.Irc.IrcMember import *
from ChatNx.ChatNxCommand import *
import logging
import os
import asyncio

def enqueue_command(client):
    command_id = os.urandom(24).hex()
    msg_id = os.urandom(24).hex()
    
    cmd = ChatNxCommand(command_id, 'jump', IrcMessage(msg_id, IrcMember("Testy", "#2233FF"), "TestChannelX", "!jump"))
    
    try:
        client.enqueue(cmd)
    except TypeError:
        print("Failed to enqueue item.")
        return None

    return cmd

async def main():

    test_logger = logging.getLogger('test_logger')
    test_logger.setLevel(logging.DEBUG)
    test_logger.addHandler(logging.StreamHandler())

    client = ChatNxQueueReceiverClient("127.0.0.1", logger=test_logger)

    client.connect()

    await asyncio.sleep(3)

    if not enqueue_command(client):
        print("Test aborted!")
        return

    await asyncio.sleep(3)

    queue_status = await client.fetch_status()

    print(f'Queue Status: {queue_status.to_json()}')

    await asyncio.sleep(3)

    client.clear_queue()

    await asyncio.sleep(3)

    cmd = enqueue_command(client)

    if not cmd:
        print("Test aborted!")
        return

    await asyncio.sleep(3)

    client.set_complete(cmd.id)

    await asyncio.sleep(3)

    client.disconnect()

    print("Test completed!")

    
asyncio.run(main())