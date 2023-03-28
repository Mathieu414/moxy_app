import pandas as pd
import xml.etree.cElementTree as ET
import re


def getvalueofnode(node):
    """ return node text or None """
    return node.text if node is not None else None


def parse_xml(content):
    """ main """
    print("--parse_xml--")

    ns = {"doc": "urn:schemas-microsoft-com:office:spreadsheet"}

    root = ET.fromstring(content)

    data = []
    for i, node in enumerate(root.findall('.//doc:Row', ns)):
        if i > 15:
            data.append({'Temps': getvalueofnode(node.find('doc:Cell[1]/doc:Data', ns)),
                         "Consommation d'Oxygène": getvalueofnode(node.find('doc:Cell[4]/doc:Data', ns)),
                         "Fréquence cardiaque": getvalueofnode(node.find('doc:Cell[12]/doc:Data', ns))})

    return (pd.DataFrame(data))
