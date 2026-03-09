from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter, FuzzyWordCompleter, DynamicCompleter

import inojet_commands as commands


def build_command_dict(tree):
    result = {}
    for key, value in tree.items():
        if isinstance(value, dict):
            result[key] = build_command_dict(value)
        elif isinstance(value, commands.Command):
            if callable(value.completer):
                result[key] = DynamicCompleter(lambda c=value.completer: FuzzyWordCompleter(c()))
            else:
                result[key] = value.completer  # None or a Completer instance
        else:
            result[key] = None
    return result


mainCompleter = NestedCompleter.from_nested_dict(build_command_dict(commands.available_commands))

session = PromptSession()