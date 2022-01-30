import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class TwitchConnectionSettings(object):
    """Encapsulates Twitch IRC connection settings."""

    def __init__(self, channel: str, auth_token: str, bot_user_name = ''):
        self.channel = channel
        self.auth_token = auth_token
        self.bot_user_name = bot_user_name or channel


class TwitchConnectionSettingsJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if not isinstance(object, TwitchConnectionSettings):
            return json.JSONEncoder.default(self, object)
        
        return { "__type__": type(object).__name__, "channel": object.channel, "auth_token": object.auth_token, "bot_user_name": object.bot_user_name }

class TwitchConnectionSettingsJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'TwitchConnectionSettings':
            return dct

        channel = dct['channel'] if 'channel' in dct else ''
        auth_token = dct['auth_token'] if 'auth_token' in dct else ''
        bot_user_name = dct['bot_user_name'] if 'bot_user_name' in dct else ''

        return TwitchConnectionSettings(channel, auth_token, bot_user_name)