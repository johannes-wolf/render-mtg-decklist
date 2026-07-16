#!/usr/bin/python

import typst
import mtg_parser as mtg
import argparse
import requests
import urllib
import httpx
import json
from collections import defaultdict
from os import path, mkdir
from pathlib import Path
from functools import cmp_to_key


image_dir = Path("./images/")
image_dir.mkdir(parents=True, exist_ok=True)

client = mtg.HttpClientFacade(httpx.Client(timeout=10.0))
headers = {
    'User-Agent': 'MTG Deck Renderer',
}


def image_filename(set_code, collector_number):
    return image_dir / f"{set_code}-{collector_number}.jpg"


def image_url(set_code, collector_number, name):
    url = f"https://api.scryfall.com/cards/{set_code}/{collector_number}"
    print(f"Loading card: {url}")
    card_object = json.loads(requests.get(url, headers=headers).content)

    # Fall back to searching the card by name
    if card_object["object"] == "error":
        print(f"Error finding card {set_code}/{collector_number}, falling back to name '{name}'.")

        url_args = urllib.parse.urlencode({"exact": name})
        url = f"https://api.scryfall.com/cards/named?{url_args}"
        card_object = json.loads(requests.get(url, headers=headers).content)
        if not "image_uris" in card_object:
            raise RuntimeError(f"Error finding card object: {set_code}/{collector_number} name: {name}")

        if card_object["object"] == "error":
            raise RuntimeError(f"Error: {card_object["details"]}")

    if "card_faces" in card_object:
        for face in card_object["card_faces"]:
            if "image_uris" in face:
                return face["image_uris"]["normal"]
    return card_object["image_uris"]["normal"]


def download_image(set_code, collector_number, name):
    filename = image_filename(set_code, collector_number)
    if not filename.exists():
        data = requests.get(image_url(set_code, collector_number, name), headers=headers).content

        with open(image_filename(set_code, collector_number), "wb") as f:
            f.write(data)

    return str(filename)


def sort_lands_back(cards):
    return sorted(cards, key=lambda card: card["is_land"])


def pair_stacks(cards):
    stacks = defaultdict(list)

    for card in cards:
        stacks[card["count"]].append(card)

    grouped = stacks[4];
    stacks[4] = []

    for i in [3, 2]:
        while len(stacks[i]) > 0:
            card = stacks[i].pop(0)
            grouped.append(card)
            if len(stacks[4 - i]) > 0:
                other = stacks[4 - i].pop(0)
                grouped.append(other)

    for rest in stacks.values():
        grouped += rest

    return grouped


def load_decklist(decklist):
    cards = mtg.parse_deck(decklist, client)

    mainboard = []
    sideboard = []

    for card in cards:
        number = card.number.lower()
        extension = card.extension.lower()
        name = card.name
        image = download_image(extension, number, name)

        item = { "count": card.quantity, "is_land": bool("land" in card.tags), "image": image }
        if "sideboard" in card.tags:
            sideboard.append(item)
        elif not "maybeboard" in card.tags:
            mainboard.append(item)


    return sort_lands_back(pair_stacks(mainboard)), sort_lands_back(pair_stacks(sideboard))


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
