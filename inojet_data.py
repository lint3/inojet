from dataclasses import dataclass, asdict
from typing import Any
import json
from os import path

import inojet_logger as log
import inojet_workspaces as ws

DEFAULT_CONFIG_PATH = ""
CONFIG_FILENAME = "config.json"

@dataclass
class Customer:
    id: int
    name: str
    guid: str
    has_active_wo: bool

@dataclass
class Assembly:
    name: str
    customer_id: int

@dataclass
class Rev:
    guid: str
    rev_name: str
    assembly_name: str



class DataStore:
    def __init__(self):
        self.customers_by_id: dict[int, Customer] = {}
        self.customers_by_name: dict[str, Customer] = {}

        self.assemblies_by_name: dict[str, Assembly] = {}
        self.assemblies_by_customer: dict[int, list[Assembly]] = {}

        self.revs_by_guid: dict[str, Rev] = {}
        self.revs_by_assembly: dict[str, list[Rev]] = {}

        self.other_data: dict[str, Any] = {}
        self.other_data["config_path"] = path.join(DEFAULT_CONFIG_PATH, CONFIG_FILENAME)

        self.workspace: ws.Workspace = ws.Workspace()

    def set_data(self, key: str, val) -> None:
        self.other_data[key] = val

    def get_data(self, key) -> Any:
        if key in self.other_data:
            return self.other_data[key]
        else:
            log.log("Could not retrieve data!", "e")
            return ""


    def add_customer(self, customer: Customer) -> None:
        self.customers_by_id[customer.id] = customer
        self.customers_by_name[customer.name] = customer

    def add_assembly(self, assembly: Assembly) -> None:
        self.assemblies_by_name[assembly.name] = assembly
        self.assemblies_by_customer.setdefault(assembly.customer_id, []).append(assembly)

    def add_rev(self, rev: Rev) -> None:
        self.revs_by_guid[rev.guid] = rev
        self.revs_by_assembly.setdefault(rev.assembly_name, []).append(rev)


    def get_assembly_by_name(self, assembly_name: str) -> Assembly | None:
        return self.assemblies_by_name.get(assembly_name)

    def get_assemblies_by_customer(self, customer_id: int) -> list[Assembly]:
        return self.assemblies_by_customer.get(customer_id, [])

    def get_revs_by_assembly(self, assembly_name: str) -> list[Rev]:
        return self.revs_by_assembly.get(assembly_name, [])

    def guid_lookup_by_assemblyrev(self, assembly_name: str, rev_name: str) -> str:
        if rev_name in self.revs_by_assembly.get(assembly_name, []):
            return self.revs_by_assembly[assembly_name][rev_name].guid
        else:
            raise NameError("Failed to look up GUID by assy and rev name!")

    def export_dict(self) -> dict[str, Any]:
        return {
            "customers": [asdict(c) for c in self.customers_by_id.values()],
            "assemblies": [asdict(a) for a in self.assemblies_by_name.values()],
            "revs": [asdict(r) for r in self.revs_by_guid.values()],
            "other_data": self.other_data
        }

    def save_to_disk(self) -> None:
        config_path = self.get_data("config_path")
        with open(config_path, "w") as dataFile:
            json.dump(self.export_dict() | {"workspaces": [self.workspace.export_dict()]}, dataFile, indent=2)
        log.d(f"Saved to {config_path}")

    @classmethod
    def replace_all_from_disk(cls, load_path: str | None) -> "DataStore":
        if load_path is None:
            load_path = path.join(DEFAULT_CONFIG_PATH, CONFIG_FILENAME)
            log.i(f"Assumed default path of {load_path}")

        with open(load_path, "r") as dataFile:
            data = json.load(dataFile)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data) -> "DataStore":
        store = cls()

        for c in data.get("customers", []):
            store.add_customer(Customer(**c))
        log.i(f"Loaded {len(data.get('customers', []))} customers")
        for a in data.get("assemblies", []):
            store.add_assembly(Assembly(**a))
        for r in data.get("revs", []):
            store.add_rev(Rev(**r))
        log.i(f"Loaded {len(data.get('revs', []))} revs of {len(data.get('assemblies', []))} assemblies")

        store.other_data = data.get("other_data", {})
        log.i(f"Loaded {len(data.get('other_data', {}))} other data items")

        workspaces = data.get("workspaces", [])
        if workspaces:
            store.workspace = ws.Workspace.from_dict(workspaces[0])

        return store


d = DataStore()
