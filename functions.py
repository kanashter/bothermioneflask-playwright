from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import pandas as pd

u = "dumps_mcgee"
p = "Newpassword1"

def get_max_pages(page):
    soup = BeautifulSoup(page.content(), 'html.parser')
    pages = soup.find("ol", { "class": "pagination actions" })
    all_pages = []
    for li in pages.findAll('li'):
        all_pages.append(li.text)
    max_pages = int(all_pages[-2])
    return [*range(2, max_pages+1)]

def get_fics(page):
    breaking = False
    all_fics = []
    soup = BeautifulSoup(page.content(), 'html.parser')
    works = soup.find("ol", { "class": "reading work index group" })
    fics = works("li", recursive=False)
    count = 0
    for i in fics:
        try: 
            fic_details = fic_check(i)
        except: 
            continue
        if fic_details["dt"] < datetime(2023, 1, 1).date(): 
            breaking = True
            break
        else: 
            all_fics.append(fic_details)
    return all_fics, breaking

def fic_check(soup):
    title_array = []
    character_array = []
    freeform_array = []
    heading = soup.find("h4", { "class": "heading"})
    title_details = heading.findChildren("a", recursive=False)
    for i in title_details:
        title_array.append(i.text)
    try:
        relationships = []
        all_relationships = soup("li", { "class": "relationships" })
        for i in all_relationships: 
            relationships.append(i.text)
    except:
        relationships = "NONE"
    characters = soup.findAll("li", { "class": "characters" })
    for i in characters:
        character_array.append(i.text)

    freeforms = soup.findAll("li", { "class": "freeforms"})
    for i in freeforms:
        freeform_array.append(i.text)
    
    visited = soup.find("h4", {"class": "viewed heading"})
    visited_text = visited.text
    match = re.search(r'\d{2}\s.*[A-Za-z]{3}\s\d{4}', visited_text)
    dtstr = match.group(0)
    dt = datetime.strptime(dtstr, "%d %b %Y").date()
    if "once" in visited_text: 
        visited_count = 1
    elif "Deleted" in visited_text: 
        visited_count = 1
    else: 
        match = re.search(r'.*[A-Za-z]{7}\s[^\s]+\s.*[A-Za-z]{4}', visited_text)
        short_visited = match.group(0)
        numbers = re.search(r'\d+', short_visited)
        visited_count = int(numbers.group(0))

    word_count = int(soup.find("dd", { "class": "words"}).text.replace(',', ''))

    details = {
        "title": title_array[0],
        "author": title_array[1],
        "relationship": relationships,
        "characters": character_array,
        "word_count": word_count,
        "tags": freeform_array,
        "visited": visited_count,
        "dt": dt
    }
    return details

def create_final_packet(data, username): 
    frame = pd.DataFrame(data)
    most_visited = frame[frame.visited == frame.visited.max()]
    total_words = frame.word_count.sum()
    total_fics = len(frame)
    total_reads = frame.visited.sum()
    all_relations = []
    all_characters = []
    all_tags = []
    for i in data:
        for x in i["relationship"]: 
            all_relations.append(x)
        for x in i["characters"]:
            all_characters.append(x)
        for x in i["tags"]:
            all_tags.append(x)
    relations_df = pd.DataFrame(all_relations)[0].value_counts().head(5).index.tolist()
    characters_df = pd.DataFrame(all_characters)[0].value_counts().head(5).index.tolist()
    tags_df = pd.DataFrame(all_tags)[0].value_counts().head(5).index.tolist()
    mv = {
        "title": most_visited.iloc[0].title,
        "author": most_visited.iloc[0].author,
        "count": int(most_visited.iloc[0].visited),
        "relations": relations_df,
        "characters": characters_df,
        "tags": tags_df
    }
    return_data = {
        "username": username,
        "total_words": int(total_words),
        "total_fics": int(total_fics),
        "total_reads": int(total_reads),
        "most_visited": mv,
    }
    return return_data




def run(playwright: Playwright, username, password):
    chromium = playwright.chromium # or "firefox" or "webkit".
    browser = chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://archiveofourown.org/users/login")
    page.locator('#user_login').click()
    page.fill('#user_login', username)
    page.locator("#user_password").click()
    page.fill("#user_password", password)
    page.locator('[value=\"Log in\"]').click()
    time.sleep(1)
    page.goto(f"https://archiveofourown.org/users/{username}/readings")
    max_pages = get_max_pages(page)
    all_details = []
    all_fics, breaking = get_fics(page)
    all_details.extend(all_fics)
    if breaking: 
        pass
    else: 
        for i in max_pages: 
            page.goto(f"https://archiveofourown.org/users/{username}/readings?page={i}")
            all_fics, breaking = get_fics(page)
            all_details.extend(all_fics)
            if breaking: 
                break
    final_packet = create_final_packet(all_details, username)
    context.close()
    browser.close()
    return final_packet


def collect_data(u, p):
    with sync_playwright() as playwright: 
        data = run(playwright, u, p)
    return data


#TODO: Parsing final data is proving to be a headache, sort it out
#COMPLETE: Logging in functioning again (fuk u cloudflare/ao3)