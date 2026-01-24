import os
import sdmdata.inaturalist as inaturalist
import sdmdata.gbif as gbif
import sdmdata.speciesLink as speciesLink
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd



from concurrent.futures import ThreadPoolExecutor

def fetch_all(
    species_names: list,
    gbif_keys: list,
    inat_ids: list,
    country: str = None,
    year_range: tuple = None,
    lat_min: float = None,
    lat_max: float = None,
    lon_min: float = None,
    lon_max: float = None
    ):
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_gbif = executor.submit(
            gbif.get_occurrences_by_key,
            gbif_keys,
            country,
            year_range,
            lat_min,
            lat_max,
            lon_min,
            lon_max
        )

        f_inat = executor.submit(
            inaturalist.get_observations_by_id,
            inat_ids,
            country,
            year_range,
            lat_min,
            lat_max,
            lon_min,
            lon_max
        )

        f_specieslink = executor.submit(
            speciesLink.get_occurrences_by_name,
            species_names,
            country,
            year_range,
            lat_min,
            lat_max,
            lon_min,
            lon_max
        )

        gbif_data = f_gbif.result()
        inat_data = f_inat.result()
        specieslink_data = f_specieslink.result()

    return gbif_data, inat_data, specieslink_data


def get_occurrences(
    species_names: list,
    gbif_keys: list,
    country: str = None,
    year_range: tuple = None,
    lat_min: float = None,
    lat_max: float = None,
    lon_min: float = None,
    lon_max: float = None
):
    inat_ids = inaturalist.get_species_ids(species_names)
    print("Fetched species IDs.")
    print(f"GBIF keys: {gbif_keys}")
    print(f"iNaturalist IDs: {inat_ids}")
    gbif_data, inat_data, specieslink_data = fetch_all(
        species_names,
        gbif_keys,
        inat_ids,
        country,
        year_range,
        lat_min,
        lat_max,
        lon_min,
        lon_max
    )
    df_inat = pd.DataFrame(inat_data)
    df_specieslink = pd.DataFrame(specieslink_data)

    df = pd.concat(
        [gbif_data, df_inat, df_specieslink],
        ignore_index=True
    )
    
    directory = "all_occurrences"
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    df.to_csv(f'{directory}/{str.join(", ", species_names)}.csv', index=False)
    return "all occurrences saved to all_occurrences/all_occurrences.csv"