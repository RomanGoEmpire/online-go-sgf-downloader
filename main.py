import logging
import os
import time
from datetime import datetime
from functools import lru_cache
from random import randint

import requests
from dotenv import load_dotenv
from sgfmill import sgf

SGF_URL = "https://online-go.com/api/v1/games/{}/sgf"
RATE_LIMIT_DURATION = 61

START_ID = 16
END_ID = 70776128


def fetch_sgf(game_id: int) -> str:
    response = requests.get(SGF_URL.format(game_id))

    if response.status_code == requests.codes.ok:
        return response.content.decode()
    elif response.status_code == requests.codes.too_many_requests:
        time.sleep(RATE_LIMIT_DURATION)
        logging.info("Sleeping")
        return fetch_sgf(game_id)
    else:
        logging.warning(f"Can't fetch {game_id}: {response.content.decode()}")
        return ""


def safe_get(root, key, default=None):
    try:
        return root.get(key)
    except KeyError:
        return default


def save_to_db(game_id: int, sgf_string: str) -> None:
    game = sgf.Sgf_game.from_string(sgf_string)
    root = game.root
    name = safe_get(root, "GN")
    date = f"{datetime.strptime(safe_get(root, "DT"), "%Y-%m-%d").isoformat()}Z"
    size = game.get_size()
    komi = game.get_komi()
    rules = safe_get(root, "RU")
    handicap = safe_get(root, "HA", 0)
    time = safe_get(root, "TM")
    overtime = safe_get(root, "OT")
    winner = game.get_winner()
    result = safe_get(root, "RE")

    # player info
    white_player = game.get_player_name("w")
    white_rank = safe_get(root, "WR")
    black_player = game.get_player_name("b")
    black_rank = safe_get(root, "BR")

    query = f"""
           CREATE game:{game_id} SET
               game_name = "{name}",
               date = <datetime>'{date}',
               size = {size},
               komi = {komi},
               rules = "{rules}",
               handicap = {handicap},
               time = {time},
               overtime = "{overtime}",
               winner = "{winner}",
               result = "{result}",
               white_player = "{white_player}",
               white_rank = "{white_rank}",
               black_player = "{black_player}",
               black_rank = "{black_rank}",
               raw_data = "{sgf_string.replace("\n", "")}"
       """

    db_url, headers, auth = credentials()
    response = requests.post(db_url, headers=headers, auth=auth, data=query)
    if response.status_code == requests.codes.ok and response.json()[0]["status"] == "OK":
        logging.info(f"Saving {game_id} successfull")
    else:
        logging.error(f"{response.status_code}: {response.json()}")


def download_sgf() -> None:
    game_id = randint(START_ID, END_ID)
    logging.info(f"Fetching {game_id}")

    sgf_string = fetch_sgf(game_id)

    if not sgf_string:
        return

    save_to_db(game_id, sgf_string)


@lru_cache
def credentials() -> tuple[str, dict, tuple[str, str]]:
    db_url = f"{os.getenv("DB_URL")}/sql"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "surreal-NS": f"{os.getenv("SURREAL_NS")}",
        "surreal-DB": f"{os.getenv("SURREAL_DB")}",
    }
    auth = (f"{os.getenv("SURREAL_USER")}", f"{os.getenv("SURREAL_PASSWORD")}")
    return db_url, headers, auth


def main() -> None:
    load_dotenv()
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename=f'logs/{datetime.now().strftime("%Y-%m-%d")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    while True:
        download_sgf()


if __name__ == '__main__':
    main()
