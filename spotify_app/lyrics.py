import pandas as pd
import requests
import logging
import datetime
import string

from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from difflib import SequenceMatcher
from lyricsgenius import Genius

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


def freak_lyrics(session: requests.Session,
                 band: str, song: str, min_similarity=0.5) -> tuple:

    root_url = "https://www.lyricsfreak.com"
    search_stem = "/search.php?q="

    url = root_url + search_stem + quote_plus(song)
    response = session.get(url)
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

    return (lyrics, max_score, url)


def genius_lyrics(genius: Genius, artist: list,
                  band: str, song: str, min_similarity=0.5) -> tuple:

    def clean_genuis_lyrics(lyrics: str) -> str:
        lyrics_start = lyrics.find('Lyrics')
        newline_start = lyrics.find('\n')
        if lyrics_start == -1 or lyrics_start > newline_start:
            lyrics_start = 0
        else:
            lyrics_start = lyrics_start + len('Lyrics')

        lyrics_end = lyrics.rfind('You might also like')
        newline_end = lyrics.rfind('\n')
        if lyrics_end == -1 or lyrics_end < newline_end:
            lyrics_end = len(lyrics)

        cleaned = lyrics[lyrics_start:lyrics_end]
        cleaned = cleaned.removeprefix('\n')
        cleaned = cleaned.removesuffix('Embed')
        cleaned = cleaned.rstrip(string.digits)

        return cleaned

    if not artist:
        artist_search = genius.search_artist(band, include_features=True)
        if artist_search is not None:
            artist.append(artist_search)
    elif band != artist[0].name:
        artist.clear()
        artist_search = genius.search_artist(band, include_features=True)
        if artist_search is not None:
            artist.append(artist_search)

    if not artist:
        return ('', -4, '')

    closest_song = None
    max_score = 0

    for track in artist[0].songs:
        score = string_likeness(song, track.title)
        if score < min_similarity:
            continue
        if score > max_score:
            max_score = score
            closest_song = track
        if score == 1:
            break

    if max_score >= min_similarity:
        lyrics = clean_genuis_lyrics(closest_song.lyrics)
        url = closest_song.url
    else:
        return ('', -4, '')

    return (lyrics, max_score, url)


def search_gen(search_terms: pd.DataFrame,
               max_searches=10_000, verbose=False):

    session = requests.Session()
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
                yield searches
                searches = 0
            searches += 1

            lyrics, status, url = freak_lyrics(session, band, song)

            if status <= -200:
                logging.critical("No longer returning 200\n" /
                                 f"{band}, {song}, {status}, {url}")
                print("No longer returning 200")
                yield searches
                return

            # print(status, url)

            if lyrics:
                search_terms.at[index, 'lyrics'] = ' '.join(lyrics)

            search_terms.at[index, 'status'] = status
            search_terms.at[index, 'url'] = url

            if verbose:
                print(status, url, lyrics[:1])
            logging.info(f"{band}, {song}, {status}, {url}")

    except Exception as e:
        logging.critical(f"{str(e)}\n")
        print(str(e))
        yield searches
        return

    yield searches
    return


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    search_terms = pd.read_pickle('data/final/lyrics.pkl')
    total_searches = 0
    for searches in search_gen(search_terms, 10, verbose=True):
        total_searches = total_searches + searches
        if total_searches > 30:
            break
    search_terms.to_pickle('data/final/lyrics.pkl')
    end_time = datetime.datetime.now()

    print(end_time - start_time)
