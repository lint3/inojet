from typing import Iterable
from prompt_toolkit import PromptSession
from prompt_toolkit.completion.base import CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter, NestedCompleter, FuzzyWordCompleter, Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle

import inojet_commands as commands
import inojet_data as ds

# class command_completer(Completer):
#     def __init__(self, state):
#         self.state = state
    
#     def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        

def build_command_dict(tree):
    result = {}
    for key, value in tree.items():
        if isinstance(value, dict):
            result[key] = build_command_dict(value)
        else:
            result[key] = None
    return result


def rebuild_completions(assemblies: list[ds.Assembly], customers: list[ds.Customer]):
    result = build_command_dict
    



assemblyList = []
customerList = []
assemblyCompleter = FuzzyWordCompleter(assemblyList)
customerCompleter = FuzzyWordCompleter(customerList)
mainCompleter = NestedCompleter.from_nested_dict(build_command_dict(commands.available_commands))

session = PromptSession()