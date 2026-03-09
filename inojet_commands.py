import os
import time

import inojet_requests as requests
import inojet_data as ds
import inojet_workspaces as ws
import inojet_logger as log


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
    log.i("Found " + str(len(refreshed_customers)) + " customers")
    ds._d.set_data("customers_last_updated", int(time.time()))

    for new_customer in refreshed_customers:
        ds._d.add_customer(new_customer)

def refresh_assemblies_revs(args: list[str]) -> None:
    if not verify_length(args, 1):
        return
    
    refreshed_assemblies, refreshed_revs = requests.fetch_assemblyrevs(int(args[0]))
    # TODO: Check if custno is valid and handle customer name

    log.i("Found " + str(len(refreshed_assemblies)) + " assemblies with " + str(len(refreshed_revs)) + " revs")

    for new_assembly in refreshed_assemblies:
        ds._d.add_assembly(new_assembly)
    for new_rev in refreshed_revs:
        ds._d.add_rev(new_rev)

def handle_data_config(args: list[str], key: str) -> None:
    if len(args) == 1:
        ds._d.set_data(key, args[0])
    elif len(args) == 0:
        log.r(ds._d.get_data(key))
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
            ds._d.set_data("config_path", args[0])
            log.i("Set file path")
    elif len(args) == 0:
        log.r(ds._d.get_data("config_path"))
    else:
        log.w("Too many args!")
        
def config_save(args: list[str]) -> None:
    if len(args) == 0:
        ds._d.save_to_disk()
    elif len(args) == 1:
        config_path(args)
        ds._d.save_to_disk()
    else:
        log.w("Too many args!")

def config_load(args: list[str]) -> None:
    if len(args) == 0:
        ds._d = ds._d.replace_all_from_disk(None)
    elif len(args) == 1:
        ds._d.replace_all_from_disk(args[0])
    else:
        log.w("Too many args!")

def retrieve_doc(args: list[str]) -> None:
    if len(args) == 2:
        log.e("DUMMY get doc " + str(args[1]) + " for assy " + str(args[0]))
    elif len(args) == 3:
        log.e("DUMMY get doc " + str(args[2]) + " for " + str(args[0]) + " " + str(args[1]))
    else:
        log.w("Bad input for retrieve_doc!")

def com(args: list[str]) -> None:
    log.e("COM: Not implemented!")

def set_workspace_rev(args: list[str]) -> None:
    pass


def set_workspace_path(args: list[str]) -> None:
    if len(args) == 1:
        ws.w.working_path = args[0]
        log.d("Set working path")
    elif len(args) == 0:
        log.r(ws.w.working_path)
    else:
        log.w("Too many args!")

def print_assemblies(args: list[str]) -> None:
    if len(args) == 1:
        for assy in ds._d.assemblies_by_customer[int(args[0])]:
            log.r(assy)
    elif len(args) == 0:
        for assy in ds._d.assemblies_by_name:
            log.r(assy)
    else:
        log.w("Too many args!")

def print_customers(args: list[str]) -> None:
    if verify_length(args, 0):
        for customer in ds._d.customers_by_id.items():
            log.r(customer[1].name)

def leave(args: list[str]) -> None:
    log.i("Goodbye.")
    exit()

available_commands = {
    "session": {
        "begin": None
    },
    "refresh": {
        "customers": refresh_customers,
        "assemblies": refresh_assemblies_revs
    },
    "config": {
        "token": handle_inonet_auth_token,
        "sessionid": handle_inonet_session_id,
        "username": handle_inonet_username,
        "path": config_path,
        "save": config_save,
        "load": config_load,
    }, 
    "doc": retrieve_doc,
    "com": {},
    "workspace": {
        "assembly": set_workspace_rev,
        "assy": set_workspace_rev,
        "path": set_workspace_path
    },
    "assemblies": print_assemblies,
    "customers": print_customers,
    "exit": leave
}