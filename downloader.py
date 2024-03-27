import os
import requests
import logging
import time

logging.basicConfig(level=logging.INFO)


URL = "https://online-go.com/api/v1/games/{game_id}"
PATH_PNG = "./data/png/{game_id}.png"
PATH_SGF = "./data/sgf/{game_id}.sgf"


def create_folders() -> None:
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/png", exist_ok=True)
    os.makedirs("./data/sgf", exist_ok=True)


def save_png(png: bytes, game_id: int) -> None:
    path = PATH_PNG.format(game_id=game_id)
    with open(path, "wb") as f:
        f.write(png)


def save_sgf(sgf: str, game_id: int) -> None:
    path = PATH_SGF.format(game_id=game_id)
    with open(path, "w") as f:
        f.write(sgf)


def get_png(
    game_id: int,
) -> None:
    if os.path.exists(PATH_PNG.format(game_id=game_id)):
        logging.info(f"PNG for game {game_id} already exists")
        return

    path = URL.format(game_id=game_id) + "/png"

    response = requests.get(path)

    if response.status_code == requests.codes.ok:
        logging.info(f"Got PNG for game {game_id}")
        save_png(response.content, game_id)
    elif response.status_code == requests.codes.too_many_requests:
        logging.info(f"Rate limited")
        time.sleep(61)
        get_png(game_id)  # ! try again after waiting
    elif response.status_code == requests.codes.not_found:
        logging.info(f"Game {game_id} not found")
    else:
        logging.info(f"Error getting PNG for game {game_id}")
        logging.error(response.status_code)
        logging.error(response.text)


def get_sgf(game_id: int) -> None:
    if os.path.exists(PATH_SGF.format(game_id=game_id)):
        logging.info(f"SGF for game {game_id} already exists")
        return
    path = URL.format(game_id=game_id) + "/sgf"
    response = requests.get(path)

    if response.status_code == requests.codes.ok:
        logging.info(f"Got SGF for game {game_id}")
        save_sgf(response.content, game_id)
    elif response.status_code == requests.codes.too_many_requests:
        logging.info(f"Rate limited")
        time.sleep(61)  # ! Limit are 10 requests per minute
        get_sgf(game_id)  # ! try again after waiting
    elif response.status_code == requests.codes.not_found:
        logging.info(f"Game {game_id} not found")
    else:
        logging.info(f"Error getting SGF for game {game_id}")
        logging.error(response.status_code)
        logging.error(response.text)
