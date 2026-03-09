import inojet_logger as log
import inojet_ui as ui

import inojet_commands as commands
from prompt_toolkit.shortcuts import CompleteStyle


def handle_command(command: str):
    parts = command.split()
    node = commands.available_commands
    i = 0
    for i, part in enumerate(parts):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            break
    else:
        i += 1
    
    if isinstance(node, commands.Command):
        node.handler(parts[i:])
    else:
        log.w("Invalid command")



log.log("Initializing...", 'i')

while True: # command handler may call exit()
    command = ui.session.prompt("INOJET > ", completer=ui.mainCompleter, complete_style=CompleteStyle.MULTI_COLUMN)
    handle_command(command)