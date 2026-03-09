
import requests
import json

import inojet_data as ds
import inojet_logger as log


# Get JSON from Inonet (returns parsed pythonic data)
def request_json(url, data=None) -> tuple[bool, dict]:
    myCookies = {
        "ASP.NET_SessionId": ds._d.get_data("inonet_session_id"),
        ".inoQuoteAuth": ds._d.get_data("inonet_auth_token"),
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


# Get list of "current" customers from Inonet
def fetch_current_customers() -> list[ds.Customer]:
    requestSuccess, response = request_json("https://www.theino.net/inoquote/inoCommon.aspx/FillCustomers")
    
    if requestSuccess:
        result = []

        for customer in response:
            result.append(ds.Customer(id=customer["custNo"],
                                        name=customer["custName"],
                                        guid=customer["custGuid"],
                                        has_active_wo=customer["hasactivewo"]))
        return result
    else:
        return []


# Get dict of Assemblies for a given customer from Inonet
def fetch_assemblyrevs(customer_id: int) -> tuple[list[ds.Assembly], list[ds.Rev]]:
    payload = {"custno": str(customer_id)}
    requestSuccess, response = request_json("https://www.theino.net/changeReq.aspx/getAssems", data=json.dumps(payload))
    
    if requestSuccess:
        resultAssys = []
        resultRevs = []

        for assemblyrev in response:
            assyName = assemblyrev["assembly"].split(" ")[0].strip()
            revName = assemblyrev["assembly"].split(" ")[1].strip()[1:-1]

            resultRevs.append(ds.Rev(guid=assemblyrev["pflid"],
                                     rev_name=revName,
                                     assembly_name=assyName))

            resultAssys.append(ds.Assembly(name=assyName,
                                        customer_id=customer_id))
        return resultAssys, resultRevs
    else:
        return [], []
    
def fetch_documents(assembly_full_name: str, work_order: int):
    log.e("Not implemented!")