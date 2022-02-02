from .MacroInput import *

import json
from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE

class ChatNxMacro(object):
    """A set of instructions executable by NXBT."""

    def __init__(self, instructions = [], controller_index = 0):
        self.controller_index = 0
        self.instructions = instructions

    def build(self)-> str:
        return "\n".join([i.build() for i in self.instructions])

    def total_duration(self)-> float:
        duration_sum = 0.0

        for instruction in self.instructions:
            duration_sum += instruction.seconds

        return duration_sum


class ChatNxMacroJsonEncoder(JSONEncoder):
    
    def default(self, object):
        if not isinstance(object, ChatNxMacro):
            return json.JSONEncoder.default(self, object)
        macro_input_encoder = MacroInputJsonEncoder()

        instructions_encoded = []

        for instruction in object.instructions:
            instruction_encoded = macro_input_encoder.default(instruction)
            instructions_encoded.append(instruction_encoded)

        return { "__type__": type(object).__name__, "instructions": instructions_encoded, "controller_index": object.controller_index }

class ChatNxMacroJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):

        typename = dct.get('__type__')
        
        if typename != 'ChatNxMacro':
            return dct

        instructions = []
        controller_index = dct.get('controller_index', 0)
        
        if 'instructions' in dct:
            macro_input_decoder = MacroInputJsonDecoder()
            
            for instruction_encoded in dct['instructions']:
                instruction = macro_input_decoder.decode(json.dumps(instruction_encoded))
                instructions.append(instruction)

        chat_nx_macro = ChatNxMacro()
        chat_nx_macro.instructions = instructions
        chat_nx_macro.controller_index = controller_index

        return chat_nx_macro

