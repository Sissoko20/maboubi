import re 
import pandas as pd

def parse_ubipharm_txt(txt_content):
    lines = txt_content.splitlines()
    region = None
    data = []

    for line in lines:
        # Détecter la région
        region_match = re.search(r'Pays.*R.gion\s+\d+/\w+\s+(.*)', line)
        if region_match:
            region = region_match.group(1).strip()

        # Détecter les lignes produit
        product_match = re.match(
            r'\s+([A-Z0-9]+)\s+(.+?)\s*/\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
            line
        )
        if product_match and region:
            code = product_match.group(1).strip()
            name = product_match.group(2).strip()
            cr = int(product_match.group(3))
            sales = [int(product_match.group(i)) for i in range(4, 11)]

            data.append({
                "Région": region,
                "Code Produit": code,
                "Nom Produit": name,
                "CR": cr,
                "11/25": sales[0],
                "M-1": sales[1],
                "M-2": sales[2],
                "M-3": sales[3],
                "M-4": sales[4],
                "M-5": sales[5],
                "M-6": sales[6],
            })

    return pd.DataFrame(data)
