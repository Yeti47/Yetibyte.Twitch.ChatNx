import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class MacroInput(object):
    """A single instruction to be executed by NXBT."""

    def __init__(self, input: str, seconds: float):
        self._input = input
        self._seconds = seconds

    @property
    def input(self):
        return self._input

    @property
    def seconds(self):
        return self._seconds

    def build(self)->str :
        return f'{self._input} {self._seconds:.4}s'

class MacroInputJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if not isinstance(object, MacroInput):
            return json.JSONEncoder.default(self, object)
        return { "__type__": type(object).__name__, "input": object.input, "seconds": object.seconds }

class MacroInputJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'MacroInput':
            return dct

        input = ''
        seconds = 0.0
        
        if 'input' in dct:
            input = dct['input']
        if 'seconds' in dct:
            seconds = dct['seconds']

        return MacroInput(input, seconds)
