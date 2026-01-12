import pandas as pd

region_to_communes = {
    "BAMAKO RIVE DROITE": ["Commune 5", "Commune 6"],
    "BAMAKO EST": ["Commune 1", "Commune 2", "Commune 3", "Commune 4"],
    "BAMAKO OUEST": ["Commune 4"],
    "BAMAKO CENTRE": ["Commune 1", "Commune 2", "Commune 3", "KATI"],
}

def repartir_par_communes(df_region: pd.DataFrame, communes: list, col: str = "11/25") -> pd.DataFrame:
    """
    Répartit la valeur d'une colonne entre les communes en lignes (vertical).
    """
    repartition = []
    for _, row in df_region.iterrows():
        valeur = row[col] if pd.notnull(row[col]) else 0
        part = valeur / len(communes) if len(communes) > 0 else valeur
        for commune in communes:
            repartition.append({
                "Région": row["Région"],
                "Commune": commune,
                "Code Produit": row["Code Produit"],
                "Nom Produit": row["Nom Produit"],
                col: part
            })
    return pd.DataFrame(repartition)


def repartir_par_communes_horizontal(df_region: pd.DataFrame, communes: list, col: str = "11/25") -> pd.DataFrame:
    """
    Répartit la valeur d'une colonne entre les communes en colonnes (horizontal).
    """
    df_out = df_region.copy()
    valeur_col = df_out[col].fillna(0)

    for commune in communes:
        df_out[f"{col} {commune}"] = valeur_col / len(communes)

    return df_out
