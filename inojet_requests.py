
import os
import requests
import json

import inojet_data as ds
import inojet_logger as log

DOCS = {
    "AOIT": "AoiTop",
    "AOIB": "AoiBottom",
    "AOIYCDTHA": "AoiTha",
    "AOIP": "AoiPolarity",
    "AOIR": "AoiMirtec",
    "ARY": "ArrayPdf",
    "ARY DWG": "ArrayDwg",
    "ASSYDWG": "AssemblyDrawing",
    "AXI": "AxiEngineering",
    "AXIP": "AxiProgram",
    "BOM": "Bom",
    "BRDIMG": "BoardImage",
    "CAD": "Cad",
    "CBOM": "CBom",
    "CECO": "Variance",
    "CUSTAPP": "CustomerApproval",
    "GER": "Gerbers",
    "GERBPAN": "GerberBoardHouse",
    "JIS": "JukiProgramsProduction",
    "JISE": "JukiProgramsEngineering",
    "MODCBOM": "ModifiedCustomerBom",
    "PCFAB": "PcbFabDrawing",
    "PREWI": "PrelimWorkInstructionsTts",
    "PREWIPDF": "PrelimWorkInstructionsPdf",
    "PRNT": "PrinterNPM",
    "R-I": "Review1",
    "R-II": "Review2",
    "RWK": "ReworkInstructionsTts",
    "RWKPDF": "ReworkInstructionsPdf",
    "SCH": "Schematic",
    "SOW": "StatementOfWork",
    "SPI_MIR": "SpiMir",
    "SPI_PRG": "SpiProgram",
    "STAMP": "StampPackage",
    "STGRB": "StencilGerber",
    "TCPROF": "ThermalChamberProfile",
    "TCRECIPE": "ThermalChamberRecipe",
    "VITRP": "ReflowProfileVitronics",
    "VITRR": "ReflowRecipeVitronics"
}

RELEVANT_DOCUMENTATION = [
    "ARY", "ASSYDWG", "BOM", "CAD", "CBOM", "PCFAB"
]

DERIVED_FILES = [
    "AOIR", "AXIP", "JIS"
]

PROD_TECH_OUTPUTS = [
    "AOIT", "AOIB", "AOIP", "AOIYCDTHA", "AXI", "JISE", "PREWI", "PREWIPDF", "RWK", "RWKPDF", 
]


# Get JSON from Inonet (returns parsed pythonic data)
def request_json(url, data=None) -> tuple[bool, dict | list]:
    myCookies = {
        "ASP.NET_SessionId": ds.d.get_data("inonet_session_id"),
        ".inoQuoteAuth": ds.d.get_data("inonet_auth_token"),
    }
    myHeaders = {
        "Content-Type": "application/json; charset=utf-8"
    }

    r = requests.post(url, headers=myHeaders, cookies=myCookies, data=data)

    if r.status_code == 200:
        if len(r.content) == 0:
            log.e("Server returned empty response!")
            return False, {}
        else:
            return True, r.json()["d"]

    else:
        log.e("Response failed with status " + str(r.status_code))
        return False, {}


def normalize_customer_name(name: str) -> str:
    name = name.replace("-", " ").replace(".", "").replace(",", "")
    return "".join(word.capitalize() for word in name.split())


# Get list of "current" customers from Inonet
def fetch_current_customers() -> list[ds.Customer]:
    requestSuccess, response = request_json("https://www.theino.net/inoquote/inoCommon.aspx/FillCustomers")

    if requestSuccess:
        result = []

        for customer in response:
            result.append(ds.Customer(id=customer["custNo"],
                                        name=normalize_customer_name(customer["custName"]),
                                        guid=customer["custGuid"],
                                        has_active_wo=customer["hasactivewo"]))
        return result
    else:
        return []


# Get list of AssemblyRevs for a given customer from Inonet.
# Inonet returns a flat list of AssemblyRevs (every rev of every assembly).
# Each item is parsed into a separate Assembly and Rev; assemblies are deduplicated.
def fetch_assemblyrevs(customer_id: int) -> tuple[list[ds.Assembly], list[ds.Rev]]:
    payload = {"custno": str(customer_id)}
    requestSuccess, response = request_json("https://www.theino.net/changeReq.aspx/getAssems", data=json.dumps(payload))

    if requestSuccess:
        resultAssys = []
        resultRevs = []
        seenAssys = set()

        for assemblyrev in response:
            assyName = assemblyrev["assembly"].split(" ")[0].strip()
            revName = assemblyrev["assembly"].split(" ")[1].strip()[1:-1]

            resultRevs.append(ds.Rev(guid=assemblyrev["pflid"],
                                     rev_name=revName,
                                     assembly_name=assyName))

            if assyName not in seenAssys:
                seenAssys.add(assyName)
                resultAssys.append(ds.Assembly(name=assyName,
                                               customer_id=customer_id))
        return resultAssys, resultRevs
    else:
        return [], []


# Get the list of available documents for a given assembly rev.
def fetch_document_list(pflid: str) -> list[dict]:
    payload = {"pflId": pflid, "wo": ""}
    success, response = request_json("https://www.theino.net/assemblyDash.aspx/FillReleasedDocsTable", data=json.dumps(payload))
    return response if (success and isinstance(response, list)) else []

# Retrieve and save a document file from Inonet.
def fetch_document(cust: str, file_name: str, short_code: str, save_path: str) -> None:
    file_path = f"\\\\10.4.8.11\\InoNet\\ReleasedDocs\\{short_code}\\{cust}\\{file_name}"
    params = {"fileName": file_name, "filePath": file_path}
    cookies = {
        "ASP.NET_SessionId": ds.d.get_data("inonet_session_id"),
        ".inoQuoteAuth": ds.d.get_data("inonet_auth_token"),
    }
    r = requests.get(
        "https://www.theino.net/inoquote/fileDownloadHandler.ashx",
        params=params,
        cookies=cookies,
        stream=True,
    )
    if r.status_code != 200:
        log.e(f"Download failed with status {r.status_code}")
        return
    dest = os.path.join(save_path, file_name)
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    log.r(f"Saved: {dest}")
