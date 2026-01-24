import pandas as pd
import pytest
from sdmdata.occurrence_requests import get_occurrences
from sdmdata.gbif import save_gbif_credentials, delete_gbif_credentials, get_species_autocomplete
from sdmdata.speciesLink import save_specieslink_apikey, delete_specieslink_apikey


        
def test_save_and_delete_specieslink_apikey():
    env_path = ".env"
    save_specieslink_apikey("my_api_key", env_path=str(env_path))
    
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "SPECIESLINK_APIKEY=my_api_key" in content

    delete_specieslink_apikey(env_path=str(env_path))
    
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "SPECIESLINK_APIKEY=my_api_key" not in content
        
def test_autocomplete():
    results = get_species_autocomplete("Puma concolor")
    assert isinstance(results, list)
    assert any("Puma concolor" in res["canonicalName"] for res in results)
    
def test_get_occurrences():
    species_names = ["Puma concolor"]
    gbif_keys = [2435099] 
    get_occurrences(
        species_names,
        gbif_keys,
        country="Brasil",
        year_range=(2000, 2020)
    )
    
    df = pd.read_csv('all_occurrences/Puma concolor.csv')
    assert not df.empty
    
    gbif_data = df[df['source'] == 'gbif'].to_dict('records')
    inat_data = df[df['source'] == 'inaturalist'].to_dict('records')
    specieslink_data = df[df['source'] == 'specieslink'].to_dict('records')
    
    assert isinstance(gbif_data, list)
    assert isinstance(inat_data, list)
    assert isinstance(specieslink_data, list)

def test_save_and_delete_gbif_credentials():
    env_path =  ".env"
    save_gbif_credentials("user", "email", "password")
    
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "GBIF_USER=user" in content
        assert "GBIF_EMAIL=email" in content
        assert "GBIF_PWD=password" in content

    delete_gbif_credentials()
    
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "GBIF_USER=user" not in content
        assert "GBIF_EMAIL=email" not in content
        assert "GBIF_PWD=password" not in content
        
if __name__ == "__main__":
    pytest.main()