# Third Party Imports (like Langchain)
# ! Place all third party imports here

# Built-in Imports (like os, sys)
from dotenv import load_dotenv

# ! Place all built-in imports here

# Local Imports
# ! Place all local imports here
from downloader import create_folders, get_png, get_sgf


def example():
    # ! Edit code below to test
    game_id = 60199157
    get_sgf(game_id)

    # You can also download the PNG
    get_png(game_id)

    # get multiple games
    for game_id in range(game_id, game_id + 10):
        get_sgf(game_id)
        get_png(game_id)


def main():
    load_dotenv()
    create_folders()

    # ! Example for downloading a game png and sgf
    example()


if __name__ == "__main__":
    main()
