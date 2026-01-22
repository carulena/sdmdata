import glob
import zipfile
from dotenv import load_dotenv
from pygbif import occurrences, species
import pandas as pd
import os.path

load_dotenv()
def create_query(keys: list, country: str = None, year_range: tuple = None, lat_min: float = None, lat_max: float = None, lon_min: float = None, lon_max: float = None): # type: ignore
    """Create a GBIF query dictionary.

    Args:
        keys (list): List of specie keys.
        country (str, optional): Country code to filter occurrences. Defaults to None.
        year_range (tuple, optional): Year range to filter occurrences (start_year, end_year). Defaults to None.
        lat_min (float, optional): Minimum latitude for bounding box. Defaults to None.
        lat_max (float, optional): Maximum latitude for bounding box. Defaults to None.
        lon_min (float, optional): Minimum longitude for bounding box. Defaults to None.
        lon_max (float, optional): Maximum longitude for bounding box. Defaults to None.
        """
    query = {
        "type": "and",
        "predicates": [
            {
            "type": "in",
            "key": "TAXON_KEY",
            "values": keys
            },
            {
            "type": "equals",
            "key": "HAS_COORDINATE",
            "value": True
            }
        ]
    }
    if(country):
        query["predicates"].append({
            "type": "equals",
            "key": "COUNTRY",
            "value": country
        })
    if(year_range):
        query["predicates"].append({
            "type": "greaterThanOrEquals",
            "key": "YEAR",
            "value": year_range[0]
        })
        query["predicates"].append({
            "type": "lessThanOrEquals",
            "key": "YEAR",
            "value": year_range[1]
        })
        
    if(lat_min is not None and lat_max is not None and lon_min is not None and lon_max is not None):
        query["predicates"].append({
            "type": "within",
            "geometry": f"POLYGON(({lon_min} {lat_min}, {lon_min} {lat_max}, {lon_max} {lat_max}, {lon_max} {lat_min}, {lon_min} {lat_min}))"
        })
    return query

# TODO da pra filtrar os campos direto no download? 
def get_occurrences_by_key(keys: list, country: str = None, year_range: tuple = None, lat_min: float = None, lat_max: float = None, lon_min: float = None, lon_max: float = None):
    """Get occurrences from GBIF by taxon key.

    Args:
        keys (list): List of specie keys.
        country (str, optional): Country to filter occurrences. Defaults to None.
        year_range (tuple, optional): Year range to filter occurrences (start_year, end_year). Defaults to None.
        """
    print(f"Downloading occurrences for taxonKey(s): {keys}")

    query = create_query(keys, country, year_range, lat_min, lat_max, lon_min, lon_max)

    res = occurrences.download(query)

    status = None
    while status != "SUCCEEDED":
        meta = occurrences.download_meta(res[0])
        status = meta["status"]
    
    directory = "gbif_download"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    occurrences.download_get(res[0],path=f"{directory}/")
    zip_original = f"{directory}/{res[0]}.zip"

    with zipfile.ZipFile(zip_original) as zf:
        csv_name = zf.namelist()[0]
        df = pd.read_csv(zf.open(csv_name), sep="\t")
            
    dataset = df[['species', 'scientificName', 'countryCode', 'decimalLatitude', 'decimalLongitude',
              'day', 'month', 'year']]
    dataset = dataset.drop_duplicates()
    dataset = dataset.rename(columns={
        'scientificName': 'scientificName',
        'countryCode': 'country',
        'decimalLatitude': 'latitude',
        'decimalLongitude': 'longitude',
        'day': 'day',
        'month': 'month',
        'year': 'year'
    })
    dataset['source'] = 'gbif'
    return dataset

def get_species_autocomplete(name: str):
    """Get species autocomplete from GBIF by name.

    Args:
        name (str): Specie name."""
        
    return species.name_suggest(q=name, rank="species", limit=10)

def get_species_keys(specie_name: str):
    res = species.name_suggest(q=specie_name, rank="species", limit=10)
    if res:
        return res[0]["key"]
    return 

def save_gbif_credentials(
    user: str,
    email: str,
    password: str,
    env_path: str = ".env"
):
    """
    Saves GBIF credentials to a .env file.
    """

    data = {
        "GBIF_USER": user,
        "GBIF_EMAIL": email,
        "GBIF_PWD": password
    }

    existent_lines  = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    existent_lines[k] = v
                    
    existent_lines.update(data)

    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in existent_lines.items():
            f.write(f"{k}={v}\n")

    print("GBIF credentials saved to .env file.")
    
def delete_gbif_credentials(env_path: str = ".env"):
    """
    Removes GBIF credentials from a .env file.
    """

    keys_to_remove = {"GBIF_USER", "GBIF_EMAIL", "GBIF_PWD"}

    if not os.path.exists(env_path):
        print("No .env file found.")
        return

    existent_lines = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                existent_lines[k] = v

    removed_any = False
    for key in keys_to_remove:
        if key in existent_lines:
            del existent_lines[key]
            removed_any = True

    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in existent_lines.items():
            f.write(f"{k}={v}\n")

    if removed_any:
        print("GBIF credentials removed from .env file.")
    else:
        print("No GBIF credentials found in .env file.")
    

def delete_file_if_exists():
    """Delete a file if it exists.

    Args:
        file_path (str): Path to the file to be deleted.
    """
    directory = "gbif_download"
    files = glob.glob(f"{directory}/*")
    for f in files:
        os.remove(f)