import inojet_data as ds

@classmethod
def from_dict(cls, data: dict[str, str]) -> "Workspace":
    w = cls()
    w.rev = data["rev"]
    w.working_path = data["working_path"]
    return w

class Workspace:
    def __init__(self, rev: ds.Rev | None = None):
        self.rev: ds.Rev | None = rev
        self.working_path: str = ""

    def export_dict(self) -> dict[str, str]:
        result = {}
        result["rev"] = self.rev
        result["working_path"] = self.working_path
        return result



w: Workspace = Workspace()