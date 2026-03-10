import os
import time
from dataclasses import dataclass
from typing import Callable

import inojet_requests as requests
import inojet_data as ds
import inojet_logger as log


@dataclass
class Command:
    handler: Callable[[list[str]], None]
    completer: Callable[[], list[str]] | None = None


CUSTOMER_UPDATE_THRESHOLD_MILLIS = 172800000 # 2 days


def verify_length(arr: list, expectedLength: int) -> bool:
    if len(arr) == expectedLength:
        return True
    elif len(arr) > expectedLength:
        log.w("Too many args!")
        return False
    else:
        log.w("Too few args!")
        return False

def refresh_customers(args: list[str]) -> None:
    if not verify_length(args, 0):
        return
    
    refreshed_customers: list[ds.Customer] = requests.fetch_current_customers()
    log.i(f"Found {len(refreshed_customers)} customers")
    ds.d.set_data("customers_last_updated", int(time.time()))

    for new_customer in refreshed_customers:
        ds.d.add_customer(new_customer)

def refresh_assemblies_revs(args: list[str]) -> None:
    if not verify_length(args, 1):
        return
    
    if args[0].isdigit():
        customer_id = int(args[0])
    else:
        customer = ds.d.customers_by_name.get(args[0])
        if customer is None:
            log.w(f"No customer found with name '{args[0]}'")
            return
        customer_id = customer.id

    refreshed_assemblies, refreshed_revs = requests.fetch_assemblyrevs(customer_id)

    log.i(f"Found {len(refreshed_assemblies)} assemblies with {len(refreshed_revs)} revs")

    for new_assembly in refreshed_assemblies:
        ds.d.add_assembly(new_assembly)
    for new_rev in refreshed_revs:
        ds.d.add_rev(new_rev)

def handle_data_config(args: list[str], key: str) -> None:
    if len(args) == 1:
        ds.d.set_data(key, args[0])
    elif len(args) == 0:
        log.r(ds.d.get_data(key))
    else:
        log.w("Too many args!")

def handle_inonet_auth_token(args: list[str]) -> None:
    handle_data_config(args, "inonet_auth_token")

def handle_inonet_session_id(args: list[str]) -> None:
    handle_data_config(args, "inonet_session_id")

def handle_inonet_username(args: list[str]) -> None:
    handle_data_config(args, "inonet_username")

def config_path(args: list[str]) -> None:
    if len(args) == 1:
        if not os.path.exists(args[0]):
            log.w("File path invalid")
        else:
            ds.d.set_data("config_path", args[0])
            log.i("Set file path")
    elif len(args) == 0:
        log.r(ds.d.get_data("config_path"))
    else:
        log.w("Too many args!")
        
def config_save(args: list[str]) -> None:
    if len(args) == 0:
        ds.d.save_to_disk()
    elif len(args) == 1:
        config_path(args)
        ds.d.save_to_disk()
    else:
        log.w("Too many args!")

def config_load(args: list[str]) -> None:
    if len(args) == 0:
        ds.d = ds.d.replace_all_from_disk(None)
    elif len(args) == 1:
        ds.d = ds.d.replace_all_from_disk(args[0])
    else:
        log.w("Too many args!")

def retrieve_doc(args: list[str]) -> None:
    if len(args) == 2:
        log.e(f"DUMMY get doc {args[1]} for assy {args[0]}")
    elif len(args) == 3:
        log.e(f"DUMMY get doc {args[2]} for {args[0]} {args[1]}")
    else:
        log.w("Bad input for retrieve_doc!")

def com(args: list[str]) -> None:
    log.e("COM: Not implemented!")

def set_workspace_assy(args: list[str]) -> None:
    if len(args) == 1:
        if args[0] in ds.d.assemblies_by_name:
            ds.d.workspace.assembly_name = args[0]
        else:
            log.w("Assembly not found!")
    elif len(args) == 0:
        if ds.d.workspace.assembly_name == "":
            log.r("No assembly name set!")
        else:
            log.r(ds.d.workspace.assembly_name)
    else:
        log.w("Too many args!")

def set_workspace_rev(args: list[str]) -> None:
    pass

def set_workspace_path(args: list[str]) -> None:
    if len(args) == 1:
        ds.d.workspace.working_path = args[0]
        log.d("Set working path")
    elif len(args) == 0:
        log.r(ds.d.workspace.working_path)
    else:
        log.w("Too many args!")

def print_assemblies(args: list[str]) -> None:
    if len(args) == 1:
        for assy in ds.d.assemblies_by_customer[int(args[0])]:
            log.r(assy)
    elif len(args) == 0:
        for assy in ds.d.assemblies_by_name:
            log.r(assy)
    else:
        log.w("Too many args!")

def print_customers(args: list[str]) -> None:
    if verify_length(args, 0):
        for customer in ds.d.customers_by_id.values():
            log.r(customer.name)

def leave(args: list[str]) -> None:
    log.i("Goodbye.")
    exit()

available_commands = {
    "session": {
        "begin": None
    },
    "refresh": {
        "customers": Command(refresh_customers),
        "assemblies": Command(refresh_assemblies_revs, lambda: list(ds.d.customers_by_name))
    },
    "config": {
        "token": Command(handle_inonet_auth_token),
        "sessionid": Command(handle_inonet_session_id),
        "username": Command(handle_inonet_username),
        "path": Command(config_path),
        "save": Command(config_save),
        "load": Command(config_load),
    },
    "doc": Command(retrieve_doc),
    "com": Command(com),
    "workspace": {
        "assembly": Command(set_workspace_assy, lambda: list(ds.d.revs_by_assembly)),
        "assy": Command(set_workspace_assy),
        "rev": Command(set_workspace_rev),
        "path": Command(set_workspace_path)
    },
    "assemblies": Command(print_assemblies),
    "customers": Command(print_customers),
    "exit": Command(leave)
}