
# USAGE.md

## Overview

**sdmdata** is a library designed to facilitate data management and processing for scientific and research applications.

## Getting Started

### Installation

```bash
pip install sdmdata
```

### Basic Usage

```python
import sdmdata

# Example: Download occurrences from GBIF, iNaturalist, and SpeciesLink

species_names = ["Panthera onca", "Lynx rufus"]
sdmdata.get_occurrences(
    species_names,
    country="Brazil",
    year_range=(2000, 2020)
)

#An excel file will be created in the working directory with the occurrence data from the three sources.

df = pd.read_excel("all_occurrences/Panthera onca,Lynx rufus.csv", sheet_name=None)

```
## Functions
- `get_occurrences(species_names, country=None, year_range=None, lat_min=None, lat_max=None)`: Fetches occurrence data for the specified species from GBIF, iNaturalist, and SpeciesLink, with optional filters for country, year range, and latitude bounds.
- `get_species_autocomplete(name)`: Retrieves a list of species suggestions from GBIF based on the provided name.
- `save_gbif_credentials(user, email, pwd)`: Saves GBIF user credentials for authenticated requests.
- `save_specieslink_apikey(apikey)`: Saves the API key for SpeciesLink requests.
- `delete_gbif_credentials()`: Deletes stored GBIF user credentials.
- `delete_specieslink_apikey()`: Deletes the stored SpeciesLink API key.

