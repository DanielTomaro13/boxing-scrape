import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

def get_wikipedia_url(search_term):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_term
    }
    response = requests.get(url, params=params)
    data = response.json()
    try:
        title = data["query"]["search"][0]["title"]
        return f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    except IndexError:
        return None

def scrape_record_table(soup):
    tables = soup.find_all("table", {"class": "wikitable"})
    for table in tables:
        if "Opponent" in str(table) and ("Record" in str(table) or "Result" in str(table)):
            try:
                df = pd.read_html(str(table))[0]
                return df
            except:
                continue
    return None

def scrape_bio_info(soup):
    bio = {
        "Height": None,
        "Reach": None,
        "Stance": None,
        "Weight": None
    }

    infobox = soup.find("table", class_="infobox")
    if infobox:
        rows = infobox.find_all("tr")
        for row in rows:
            header = row.find("th")
            data = row.find("td")
            if not header or not data:
                continue
            label = header.text.strip().lower()
            value = data.text.strip()

            if "height" in label:
                bio["Height"] = value
            elif "reach" in label:
                bio["Reach"] = value
            elif "stance" in label or "style" in label:
                bio["Stance"] = value
            elif "weight" in label:
                bio["Weight"] = value
    return bio

def clean_filename(name):
    return name.replace(" ", "_").replace(".", "").replace(",", "")

# Load fighters list
fighters_df = pd.read_csv("/Users/danieltomaro/Documents/Projects/boxing-scrape/data/fighters_to_scrape.csv")

# Create or load bios output file
bios = []

for index, row in fighters_df.iterrows():
    name = row['name']
    if not str(row['scraped']).lower() == 'true':
        print(f"\n🔍 Scraping: {name}")
        wiki_url = get_wikipedia_url(name)
        if not wiki_url:
            print(f"❌ Wikipedia page not found for {name}")
            continue

        response = requests.get(wiki_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Scrape record table
        record_df = scrape_record_table(soup)
        if record_df is not None:
            os.makedirs("records", exist_ok=True)
            filename = f"records/{clean_filename(name)}_record.csv"
            record_df.to_csv(filename, index=False)
            print(f"✅ Saved record table to {filename}")
        else:
            print(f"⚠️ No boxing record table found for {name}")

        # Scrape bio data
        bio = scrape_bio_info(soup)
        bio["Name"] = name
        bios.append(bio)
        print(f"📏 Bio scraped: {bio}")

        fighters_df.at[index, 'scraped'] = True

# Save updated fighters list
fighters_df.to_csv("fighters_to_scrape.csv", index=False)

# Save bios
if bios:
    bios_df = pd.DataFrame(bios)
    bios_df.to_csv("fighter_bios.csv", index=False)
    print("\n💾 All bios saved to fighter_bios.csv")
else:
    print("\n⚠️ No bios were scraped.")
