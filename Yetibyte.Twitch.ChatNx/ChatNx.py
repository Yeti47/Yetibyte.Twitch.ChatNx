#from SwitchConnector import SwitchConnector, ControllerTypes, Buttons, Sticks
#from MockSwitchConnector import MockSwitchConnector
#from OdysseyBot import OdysseyBot
from ChatNx.Configuration import *
from ChatNx.Irc import *
import jsonpickle
import json
import logging
import time
import asyncio
from ChatNx.QueueReceiver import *

async def main():

    #switch_connector: SwitchConnector = MockSwitchConnector()

    #switch_connector.initialize()
    #controller_index = switch_connector.create_controller(ControllerTypes.PRO_CONTROLLER)
    #switch_connector.wait_for_connection(controller_index)

    #controller_count = switch_connector.get_controller_count()
    #state = switch_connector.get_state()

    #print(f'Controller Count: {controller_count}')
    #print(f'State: {state}')

    #test_macro = """
    #B 0.1s
    #0.1s
    #A 0.3s
    #0.5s
    #"""

    #macro_id = switch_connector.macro(controller_index, test_macro, True)

    #switch_connector.remove_controller(controller_index)

    #controller_count = switch_connector.get_controller_count()
    #state = switch_connector.get_state()

    #print(f'Controller Count: {controller_count}')
    #print(f'State: {state}')

    #bot = OdysseyBot()
    #bot.run()

    macro_input = MacroInput('B', 0.2)
    nx_macro = ChatNxMacro()
    nx_macro.instructions.append(macro_input)

    js = jsonpickle.encode(nx_macro)

    print(js)

    print('####')

    encoder = MacroInputJsonEncoder()
    js_enc = json.dumps(macro_input, cls=MacroInputJsonEncoder, indent=4)

    print(js_enc)

    print(encoder.default(macro_input))

    print('______________')

    encoder = ChatNxMacroJsonEncoder()
    js_enc = json.dumps(nx_macro, cls=ChatNxMacroJsonEncoder, indent=4)

    print(js_enc)

    test_macro = ChatNxMacro()
    test_macro.instructions = [ MacroInput('B', 2.2), MacroInput('L_STICK@+100-050', 1.5), MacroInput('X Y', 0.3) ]

    print(test_macro.build())

    print('====================================')
    print('====================================')

    test_macro_a = ChatNxMacro()
    test_macro_a.instructions = [ MacroInput('A B', 0.5), MacroInput('X', 1.2) ]

    test_macro_b = ChatNxMacro()
    test_macro_b.instructions = [ MacroInput('L_STICK@+100-050', 0.5), MacroInput('Y', 1.0) ]

    command_setup_a = ChatNxCommandSetup('test', test_macro_a, PermissionLevel.ANY, cooldown_group='TestCooldown', arguments=['up', 'down', 'left', 'right'])
    command_setup_b = ChatNxCommandSetup('anotherTest', test_macro_b, PermissionLevel.MOD, cooldown_group='ModCooldown')

    cooldown_setup_a = ChatNxCooldownSetup('TestCooldown', 30.0)
    cooldown_setup_a.set_time(PermissionLevel.ANY, 15.0)

    cooldown_setup_b = ChatNxCooldownSetup('ModCooldown')
    cooldown_setup_b.set_time(PermissionLevel.MOD, 5.5)

    command_settings = ChatNxCommandProfile('TestProfile', commands=[command_setup_a, command_setup_b], cooldown_groups=[cooldown_setup_a, cooldown_setup_b])

    command_settings_encoder = ChatNxCommandProfileJsonEncoder()

    cmd_settings_json = json.dumps(command_settings, cls=ChatNxCommandProfileJsonEncoder, indent=4)

    print(cmd_settings_json)

    config_manager = ChatNxConfigManager()

    loaded_config = config_manager.load_config()

    print("=======TEST DTO SERIALIZATION: BEGIN========")

    command_queue_request = CommandQueueRequest(
        action = 'ADD',
        item_data = CommandQueueItemData(
            id = '123',
            user_name = 'Bobby',
            user_color_hex = '#FF0000',
            command = 'jump'
        )
    )

    print(command_queue_request.to_json())

    decoded_item_data = CommandQueueItemData.from_json('{ "Id": "456", "UserName": "Test", "UserColorHex": "#0000FF", "Command": "doStuff" }')

    print(decoded_item_data.user_name)

    print("=======TEST DTO SERIALIZATION: END========")

    print("=======TEST MOCK CLIENT: BEGIN========")

    irc_logger = logging.getLogger("IRC_LOGGER")
    irc_logger.addHandler(logging.StreamHandler())
    irc_logger.setLevel(logging.DEBUG)

    irc_client: IrcClient = MockIrcClient("!", 
                                          TwitchConnectionSettings("SomeTwitchChannel", "FAKE_TOKEN", "ChatNxBot"),
                                          loaded_config.command_profiles[0],
                                          irc_logger)

    irc_client.connect()

    while irc_client.is_connected():
        await asyncio.sleep(1)

    print("=======TEST MOCK CLIENT: END========")


asyncio.run(main())
#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())