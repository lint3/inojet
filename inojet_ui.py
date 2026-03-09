from typing import Iterable
from prompt_toolkit import PromptSession
from prompt_toolkit.completion.base import CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter, NestedCompleter, FuzzyWordCompleter, Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle

import inojet_commands as commands

def build_command_dict(tree):
    result = {}
    for key, value in tree.items():
        if isinstance(value, dict):
            result[key] = build_command_dict(value)
        else:
            result[key] = None
    return result



assemblyList = []
customerList = []
assemblyCompleter = FuzzyWordCompleter(assemblyList)
customerCompleter = FuzzyWordCompleter(customerList)
mainCompleter = NestedCompleter.from_nested_dict(build_command_dict(commands.available_commands))

session = PromptSession()