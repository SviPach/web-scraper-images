from bs4 import BeautifulSoup
import requests
from PIL import Image
from io import BytesIO
import time
import re
import os

def image_search():
    os.makedirs("./SearchResults/", exist_ok=True)
    search = input("Search for ('-stop' to exit): ")
    if search == "-stop":
        return

    params = {"q": search}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/127.0.0.1 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.bing.com/"
    }
    r = requests.get("http://www.bing.com/images/search", params=params, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    links_raw = soup.find("div", {"id": "mmComponent_images_2"}).find_all("li")
    time.sleep(2)

    print("Amount of raw links:", len(links_raw))
    links = []
    for link in links_raw:
        if link.has_attr("data-idx") and link.find("a", {"class": "inflnk"}) is not None:
            links.append(link)
    amount_found = len(links)

    if len(links) != 0:
        while True:
            print("Amount of images:", amount_found)
            amount = int(input("How many photos to get: "))

            if amount not in range(0, amount_found+1):
                print("Not a valid amount of photos.")
                continue
            break

        for i in range(amount):

            item = links[i]
            print(f"----------[{i+1}]:")
            print("---Item:", item)
            img_obj = requests.get(item.find("img")["src"])
            print("---Content:", img_obj.content)
            time.sleep(2)

            img_name = item.find("a", {"class": "inflnk"}).attrs["aria-label"]
            img_name = re.sub(r'[\\/*?:"<>|]', "_", img_name)
            print("---Name:", img_name)

            img = Image.open(BytesIO(img_obj.content))
            img_format = img.format.lower() if img.format is not None else "jpeg"
            print("---Format:", img_format)

            if img_format == "webp":
                img = img.convert("RGB")
                img_format = "jpeg"

            img_name += '.' + img_format

            os.makedirs("./SearchResults/" + search, exist_ok=True)
            img.save(f"./SearchResults/{search}/" + img_name, img_format)
            print("-----Success!\nSaved as:", img_name)
            print("\n")
    else:
        print("No images found")

    image_search()

image_search()