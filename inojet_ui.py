from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, NestedCompleter, FuzzyWordCompleter, DynamicCompleter

import inojet_commands as commands


class SequentialCompleter(Completer):
    """Completes successive positional arguments using a list of completer functions.
    Each function receives the list of already-completed tokens and returns candidates."""

    def __init__(self, completers):
        self.completers = completers  # list[Callable[[list[str]], list[str]]]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()
        if text.endswith(' ') or not text:
            idx = len(words)
            prior = words
        else:
            idx = len(words) - 1
            prior = words[:-1]
        if idx < len(self.completers):
            candidates = self.completers[idx](prior)
            yield from FuzzyWordCompleter(candidates).get_completions(document, complete_event)


def build_command_dict(tree):
    result = {}
    for key, value in tree.items():
        if isinstance(value, dict):
            result[key] = build_command_dict(value)
        elif isinstance(value, commands.Command):
            if value.completers:
                result[key] = SequentialCompleter(value.completers)
            elif callable(value.completer):
                result[key] = DynamicCompleter(lambda c=value.completer: FuzzyWordCompleter(c()))
            else:
                result[key] = value.completer  # None or a Completer instance
        else:
            result[key] = None
    return result


mainCompleter = NestedCompleter.from_nested_dict(build_command_dict(commands.available_commands))

session = PromptSession()
