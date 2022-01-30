import asyncio
from ChatNx.Irc.IrcClient import *
from ChatNx.Irc.IrcClientListener import *
from ChatNx.Irc.IrcMessage import *
from ChatNx.Irc.IrcMember import *
from ChatNx.Irc.TwitchIrcClient import *
from ChatNx.Configuration.TwitchConnectionSettings import *
import logging
import datetime

class TestIrcListener(IrcClientListener):
    
    def on_message_received(self, message):
        print(f'{message.timestamp} Received message by user {message.author.display_name}: {message.content}')

    def on_message_sent(self, message):
        pass

    def on_sending_message(self, message):
        pass

async def main():

    loop = asyncio.get_running_loop()

    logger = logging.Logger("TEST_LOGGER")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    channel = input("Enter Channel:")
    bot_user = input("Enter Bot User Name:")
    token = input("Enter Auth Token:")

    connection_settings = TwitchConnectionSettings(channel, token, bot_user)

    irc_client = TwitchIrcClient("!", connection_settings, logger=logger, loop=loop)

    listener = TestIrcListener()
    irc_client.add_listener(listener)

    is_connected = await irc_client.connect()

    await asyncio.sleep(1)

    if not is_connected:
        print('Connection failed. Cancelling test.')
        await irc_client.dispose()
        return

    await irc_client.send_message(f'This is a test! {datetime.datetime.now()}')

    await asyncio.sleep(1)

    print("IRC client ready. Send keyboard interrupt to quit (or close console).")

    while True:
        try:
            await asyncio.sleep(0.03)
        except KeyboardInterrupt:
            break

    if irc_client.is_connected():
        await irc_client.disconnect()


# We need to add the event loop policy WindowsSelectorEventLoopPolicy due to an issue on Windows
# which causes tasks to not be properly closed before the loop ends
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())


