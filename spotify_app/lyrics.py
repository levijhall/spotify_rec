import requests
import logging

from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from difflib import SequenceMatcher

from langdetect import detect
from langdetect import DetectorFactory
from langdetect import LangDetectException
DetectorFactory.seed = 0

logging.basicConfig(filename='app.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def lang_detect(s):
    try:
        lang = detect(s)
        return lang
    except LangDetectException:
        return ''


def clean_string(s: str) -> str:
    "Remove stop words and whitespace"
    s = s.removeprefix('·').strip()
    s = s.lower()
    if s.startswith('the '):
        s = s[4:]
    s = s.replace(' the ', '')
    s = s.replace(' ', '')
    s = s.replace("'", "")

    return s


def string_likeness(main: str, second: str) -> float:
    "Get the likeness of two strings as a percentage"

    main = clean_string(main)
    second = clean_string(second)

    seq = SequenceMatcher(None, main, second)
    match = seq.find_longest_match()

    max_length = max(map(len, [main, second]))

    if match.size == max_length:
        return 1.
    else:
        return (1. * match.size) / max_length


def find_lyrics(band: str, song: str, min_similarity=0.5) -> str:
    root_url = "https://www.lyricsfreak.com"
    search_stem = "/search.php?q="

    url = root_url + search_stem + quote_plus(song)
    response = requests.get(url)
    if response.status_code != 200:
        print(response.status_code, url)
        return [], -200, url

    soup = BeautifulSoup(response.text, 'html.parser')
    indiatables = soup.select('div.lf-list__row a')

    if not indiatables:
        # print("No results found!", url)
        return [], -1, url

    lyric_url = ''
    max_score = 0

    iterable = iter(indiatables)
    for link in iterable:
        score = string_likeness(band, link.text)
        link = next(iterable)
        if clean_string(song) in clean_string(link.text):
            if score < min_similarity:
                continue
            if score > max_score:
                max_score = score
                lyric_url = link.get('href')

    if not lyric_url:
        # print("No matching results.", url)
        return [], -2, url

    url = root_url + lyric_url
    response = requests.get(url)
    response.status_code

    if response.status_code != 200:
        # print(response.status_code, url)
        return [], -201, url

    soup = BeautifulSoup(response.text, 'html.parser')
    indiatables = soup.find('div', {'id': 'content'})

    if not indiatables:
        # print("No lyrics found!", url)
        return [], -3, url

    lyrics = []

    for div in indiatables:
        line = div.text.strip()
        if line:
            lyrics.append(line)

    return lyrics, max_score, url


def search(max_searches=10_000, verbose=False):
    global search_terms
    searches = 0

    try:
        for index, row in search_terms.iterrows():
            band = row['artist_name'].strip()
            song = row['name'].strip()
            # year = row['year']

            if row['status'] != 0:
                continue

            if row['instrumentalness'] > 0.5:
                continue

            if row['name_lang'] != 'en':
                continue

            if searches >= max_searches:
                break
            searches += 1

            lyrics, status, url = find_lyrics(band, song)

            if status <= -200:
                logging.critical("No longer returning 200\n" /
                                 f"{band}, {song}, {status}, {url}")
                print("No longer returning 200")
                return searches

            # print(status, url)

            if lyrics:
                search_terms.at[index, 'lyrics'] = ' '.join(lyrics)

            search_terms.at[index, 'status'] = status
            search_terms.at[index, 'url'] = url

            if verbose:
                print(status, url, lyrics[:1])

    except Exception as e:
        logging.critical(f"{str(e)}\n" /
                         f"{band}, {song}, {status}, {url}")
        print(str(e))
        return searches

    return searches
