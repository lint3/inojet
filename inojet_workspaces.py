class Workspace:
    def __init__(self):
        self.rev_name: str = ""
        self.assembly_name: str = ""
        self.working_path: str = ""

    def export_dict(self) -> dict[str, str]:
        result = {}
        result["rev"] = self.rev_name
        result["assembly_name"] = self.assembly_name
        result["working_path"] = self.working_path
        return result

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Workspace":
        w = cls()
        w.rev_name = data["rev"]
        w.working_path = data["working_path"]
        w.assembly_name = data["assembly_name"]
        return w
