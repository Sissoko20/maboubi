import re
import pandas as pd

MONTH_RE = re.compile(r'^\d{2}/\d{2}$')

def extract_headers(txt_content):
    """
    Extrait dynamiquement les en-têtes de ventes depuis la ligne 'Stocks / CR ...'.
    Ignore 'Stocks', '/', 'CR' et ne garde que les 7 colonnes de ventes.
    Valide que la première est bien un mois au format NN/NN.
    """
    for line in txt_content.splitlines():
        if "Stocks / CR" in line:
            tokens = re.findall(r'\S+', line)
            # tokens ex: ['Stocks', '/', 'CR', '11/26', 'M-1', 'M-2', 'M-3', 'M-4', 'M-5', 'M-6']
            # On ignore les 3 premiers et on garde le reste
            sales_headers = tokens[3:]
            # Nettoyage: enlever toute occurrence résiduelle de '/' par sécurité
            sales_headers = [h for h in sales_headers if h != '/']

            # Validation: on attend 7 colonnes de ventes
            if len(sales_headers) != 7:
                # Fallback: si la première ressemble à un mois, compléter avec M-1..M-6
                month = next((h for h in sales_headers if MONTH_RE.match(h)), None)
                if month:
                    sales_headers = [month, "M-1", "M-2", "M-3", "M-4", "M-5", "M-6"]
                else:
                    # Dernier recours: forcer un schéma standard
                    sales_headers = ["MOIS", "M-1", "M-2", "M-3", "M-4", "M-5", "M-6"]

            # Validation: la première doit être le mois courant (NN/NN)
            if not MONTH_RE.match(sales_headers[0]):
                # Si l'ordre est inversé, tenter de remettre le mois en premier
                month_idx = next((i for i, h in enumerate(sales_headers) if MONTH_RE.match(h)), None)
                if month_idx is not None and month_idx != 0:
                    sales_headers = [sales_headers[month_idx]] + [h for i, h in enumerate(sales_headers) if i != month_idx]

            return sales_headers

    # Si aucune ligne d'en-tête trouvée, fallback standard
    return ["MOIS", "M-1", "M-2", "M-3", "M-4", "M-5", "M-6"]


def parse_ubipharm_txt(txt_content):
    """
    Parser robuste:
    - Récupère dynamiquement les en-têtes de ventes (mois courant + M-1..M-6).
    - Capture Stock (optionnel) et CR.
    - Associe strictement 7 valeurs de ventes aux 7 en-têtes.
    - Évite toute colonne '/' et garantit une seule colonne de mois courant.
    """
    lines = txt_content.splitlines()
    region = None
    data = []

    headers = extract_headers(txt_content)  # 7 colonnes de ventes attendues

    for line in lines:
        # Détecter la région
        region_match = re.search(r'Pays.*R.gion\s+\d+/\w+\s+(.*)', line)
        if region_match:
            region = region_match.group(1).strip()
            continue  # passer à la ligne suivante

        # Détecter les lignes produit
        product_match = re.match(
            r'\s+([A-Z0-9]+)\s+(.+?)\s+(\d+)?\s*/\s*(\d+)\s+'   # Stock (optionnel) / CR
            r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',  # 7 colonnes de ventes
            line
        )
        if product_match and region:
            code = product_match.group(1).strip()
            name = product_match.group(2).strip()
            stock = int(product_match.group(3)) if product_match.group(3) else None
            cr = int(product_match.group(4))
            sales = [int(product_match.group(i)) for i in range(5, 12)]

            # Validation stricte: 7 en-têtes et 7 valeurs
            if len(headers) != 7 or len(sales) != 7:
                # Si mismatch, on skip ou on log selon besoin
                # Ici on skip pour éviter des colonnes fausses
                continue

            row = {
                "Région": region,
                "Code Produit": code,
                "Nom Produit": name,
                "Stock": stock,
                "CR": cr,
            }
            for h, val in zip(headers, sales):
                row[h] = val

            data.append(row)

    return pd.DataFrame(data)
