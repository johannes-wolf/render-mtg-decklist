#!/usr/bin/python

import typst
import mtg_parser as mtg
import argparse
import requests
import httpx
import json
from os import path, mkdir
from pathlib import Path


image_dir = Path("./images/")
image_dir.mkdir(parents=True, exist_ok=True)

client = mtg.HttpClientFacade(httpx.Client(timeout=10.0))
headers = {
    'User-Agent': 'MTG Deck Renderer',
}


def image_filename(set_code, collector_number):
    return image_dir / f"{set_code}-{collector_number}.jpg"


def image_url(set_code, collector_number):
    url = f"https://api.scryfall.com/cards/{set_code}/{collector_number}"
    card_object = json.loads(requests.get(url, headers=headers).content)

    print(f"Loading card: {url}")
    return card_object["image_uris"]["normal"]


def download_image(set_code, collector_number):
    filename = image_filename(set_code, collector_number)
    if not filename.exists():
        data = requests.get(image_url(set_code, collector_number), headers=headers).content

        with open(image_filename(set_code, collector_number), "wb") as f:
            f.write(data)

    return str(filename)


def sort_lands_back(cards):
    return sorted(cards, key=lambda card: card["is_land"])


def load_decklist(decklist):
    cards = mtg.parse_deck(decklist, client)

    mainboard = []
    sideboard = []

    for card in cards:
        number = card.number.lower()
        extension = card.extension.lower()
        image = download_image(extension, number)

        item = { "count": card.quantity, "is_land": bool("land" in card.tags), "image": image }
        if "sideboard" in card.tags:
            sideboard.append(item)
        elif not "maybeboard" in card.tags:
            mainboard.append(item)


    return sort_lands_back(mainboard), sort_lands_back(sideboard)


def render_decklist(mainboard, sideboard, name, date, score, output=None):
    inputs = {
        "name": "My Deck",
        "mainboard": json.dumps(mainboard),
        "sideboard": json.dumps(sideboard),
        "name": name or "unnamed deck",
        "date": date or "unknown date",
        "score": score or "0-0-0"
    }

    images = typst.compile("./template.typ",
                           output=output or "decklist.png",
                           format="png",
                           ppi=25.4,
                           sys_inputs=inputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Render MTG Decklist")

    parser.add_argument("filename")
    parser.add_argument("-d", "--date")
    parser.add_argument("-n", "--name")
    parser.add_argument("-s", "--score")
    parser.add_argument("-o", "--output")
    parser.add_argument("-D", "--debug", action="store_true")

    args = vars(parser.parse_args())

    mainboard, sideboard = load_decklist(args["filename"])
    if args["debug"]:
      with open("mainboard.json", "w") as f:
        f.write(json.dumps(mainboard))
      with open("sideboard.json", "w") as f:
        f.write(json.dumps(sideboard))

    render_decklist(mainboard,
                    sideboard,
                    args["name"],
                    args["date"],
                    args["score"],
                    output=args["output"])
