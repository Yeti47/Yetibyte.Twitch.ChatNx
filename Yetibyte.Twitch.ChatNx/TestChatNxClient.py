from ChatNx.SwitchConnector.SwitchConnector import *
from ChatNx.MockSwitchConnector import *
#from ..NxbtSwitchConnector import *
from ChatNx.ChatNxClient import *
from ChatNx.Configuration.ChatNxConfig import *
from ChatNx.Configuration.ChatNxConfigManager import *
from ChatNx.Irc.IrcClient import *
from ChatNx.Irc.MockIrcClient import *
from ChatNx.Irc.TwitchIrcClient import *
from ChatNx.QueueReceiver.ChatNxQueueReceiverClientBase import *
from ChatNx.QueueReceiver.ChatNxQueueReceiverClient import *

import asyncio
import logging

_chat_nx_client_: ChatNxClient = None

async def main():

    loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
    
    logger = logging.Logger("TEST_LOGGER")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    channel = input("Enter Channel:")
    bot_user = input("Enter Bot User Name:")
    token = input("Enter Auth Token:")

    config_manager = ChatNxConfigManager()

    config = config_manager.load_config()

    do_mock_irc = input("Mock IRC (y/n):").strip().lower() == "y"
    do_mock_switch_connector = input('Mock Switch Connector (y/n):').strip().lower() == "y"

    irc_client = MockIrcClient(config.connection_settings, config.command_profiles[0], logger) \
        if do_mock_irc \
        else TwitchIrcClient(config.command_profiles[0].prefix, TwitchConnectionSettings(channel, token, bot_user), logger, loop)

    switch_connector = MockSwitchConnector(logger) \
        if do_mock_switch_connector \
        else NxbtSwitchConnector(logger=logger)
    switch_connector.initialize()

    chat_nx = ChatNxClient(
        config, 
        config.command_profiles[0], 
        switch_connector,
        irc_client,
        ChatNxQueueReceiverClient('127.0.0.1', 4769, logger),
        logger)

    _chat_nx_client_ = chat_nx

    print("TEST: Connecting to IRC...\r\n")

    await chat_nx.connect_to_irc()

    print("TEST: Connecting to Queue Receiver...\r\n")

    chat_nx.connect_to_queue_receiver()

    print("TEST: Connecting to Nintendo Switch...\r\n")

    await chat_nx.connect_to_switch()

    print("TEST: Running ChatNx client...\r\n")

    await chat_nx.run()

    print("TEST: ChatNx client running. Send Keyboard Interrupt to quit (or close console).\r\n")
    
    while True:
        await asyncio.sleep(0.001)


# We need to add the event loop policy WindowsSelectorEventLoopPolicy due to an issue on Windows
# which causes tasks to not be properly closed before the loop ends
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as key_ex:
    
        if _chat_nx_client_:
            print("Stopping ChatNx Client...!\r\n")
            _chat_nx_client_.stop()
            print("Client stopped.\r\n")
    
        print("Goddbye!\r\n")
