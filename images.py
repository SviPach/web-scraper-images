from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
import time
import re
import os
from bcolors import Bcolors as bc

def image_search():
    os.makedirs("./SearchResults/", exist_ok=True)
    search = input(bc.HEADER + "Search for ('-stop' to exit): " + bc.ENDC)
    if search == "-stop":
        print(bc.BLUE + "Exiting..." + bc.ENDC)
        return

    params = {"q": search}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/127.0.0.1 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bing.com/"
    }
    try:
        r = requests.get("http://www.bing.com/images/search", params=params, headers=headers)
        r.raise_for_status()
    except Exception as e:
        print(bc.FAIL + "Connection error:", bc.BOLD + e.__class__.__name__ + bc.ENDC)
        return

    soup = BeautifulSoup(r.text, "html.parser")
    container = soup.find("div", {"id": "mmComponent_images_2"})

    if container is None:
        print(bc.FAIL + "Could not find image container." + bc.ENDC)
        return

    links_raw = container.find_all("li")

    time.sleep(2)

    print(bc.BLUE + "-Amount of raw links:" + bc.ENDC, len(links_raw))
    links = []
    for link in links_raw:
        if link.has_attr("data-idx") and link.find("a", {"class": "inflnk"}) is not None:
            links.append(link)

    amount = 0
    if len(links) != 0:
        while True:
            print(bc.BLUE + "-Amount of images:" + bc.ENDC, len(links))
            try:
                amount = int(input(bc.HEADER + "How many photos to get: " + bc.ENDC))
            except ValueError:
                print(bc.FAIL + "Please enter a number." + bc.ENDC)
                continue

            if amount not in range(0, len(links) + 1):
                print(bc.FAIL + "Not a valid amount of photos." + bc.ENDC)
                continue
            break

        for i in range(amount):
            item = links[i]
            print(bc.WARNING + f"----------[{i+1}]:" + bc.ENDC)
            print(bc.BLUE + "---Item:" + bc.ENDC, item)

            try:
                img_obj = requests.get(item.find("img")["src"])
                img_obj.raise_for_status()
            except Exception as e:
                print(bc.FAIL + "Failed to fetch image:", bc.BOLD + e.__class__.__name__ + bc.ENDC)
                return

            print(bc.BLUE + "---Content:" + bc.ENDC, img_obj.content)
            time.sleep(2)

            img_link = item.find("img")["src"]
            print(bc.BLUE + "---Image link:" + bc.ENDC, img_link)

            website_link = item.find("div", {"class": "img_info hon"}).find("a")["href"]
            print(bc.BLUE + "---Website link:" + bc.ENDC, website_link)

            img_name = item.find("a", {"class": "inflnk"}).attrs["aria-label"]
            img_name = re.sub(r'[\\/*?:"<>|]', "_", img_name)
            print(bc.BLUE + "---Name:" + bc.ENDC, img_name)

            img = Image.open(BytesIO(img_obj.content))
            img_format = img.format.lower() if img.format is not None else "jpeg"
            print(bc.BLUE + "---Format:" + bc.ENDC, img_format)

            if img_format == "webp":
                img = img.convert("RGB")
                img_format = "jpeg"

            img_name += '.' + img_format

            os.makedirs("./SearchResults/" + search, exist_ok=True)
            img.save(f"./SearchResults/{search}/" + img_name, img_format)
            print(bc.GREEN + "-----Success!\nSaved as:" + bc.ENDC, img_name)
            time.sleep(1)
            print("\n")
    else:
        print(bc.FAIL + "No images found" + bc.ENDC)

    print(bc.BLUE + bc.UNDERLINE + "Photos are saved in:" + bc.ENDC, "./SearchResults/" + search, "\n\n")
    time.sleep(2)
    image_search()

image_search()