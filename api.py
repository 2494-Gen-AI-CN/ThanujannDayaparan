import json
from pathlib import Path
import requests

POKEMON_URL = "https://pokeapi.co/api/v2/pokemon"
CACHE_FILE = Path(__file__).with_name("pokemon_cache.json")
POKEMON_LIMIT = 151  # first gen


def get_pokemon_data():
    # use the saved file if we already have it
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    # Else get list of Pokemon from the API
    response = requests.get(POKEMON_URL, params={"limit": POKEMON_LIMIT}, timeout=10)
    response.raise_for_status()

    pokemon_data = []
    for pokemon in response.json()["results"]:
        pokemon_response = requests.get(pokemon["url"], timeout=10)
        pokemon_response.raise_for_status()
        details = pokemon_response.json()

        stats = {stat["stat"]["name"]: stat["base_stat"] for stat in details["stats"]}

        pokemon_data.append(
            {
                "name": details["name"].title(),
                "sprite": details["sprites"]["front_default"],
                "stats": stats,
                "base_stats_total": sum(stats.values()),
            }
        )

    # write data to a cache file 
    CACHE_FILE.write_text(json.dumps(pokemon_data), encoding="utf-8")
    return pokemon_data


if __name__ == "__main__":
    data = get_pokemon_data()
    print(data[1])