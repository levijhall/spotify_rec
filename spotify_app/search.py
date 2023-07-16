import pandas as pd
import time
import datetime

from lyrics import search
from sendMail import sendMail


def read_last_n_lines(file_path, n):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        last_n_lines = lines[-n:]
        return last_n_lines


original_start = time.process_time()
total_entries = 0

batch_size = 10_000
while True:
    start_time = time.process_time()

    search_terms = pd.read_pickle('../data/final/lyrics.pkl')
    new_entries = search(batch_size)
    search_terms.to_pickle('../data/final/lyrics.pkl')

    end_time = time.process_time()

    to = ['Levi Hall <levi.j.hall@outlook.com']
    fro = ['Levi Hall <contact@levihall.com']
    subject = 'Lyrics update'

    diff = end_time - start_time
    total_diff = end_time - original_start

    total_entries = total_entries + new_entries

    diff_string = datetime.timedelta(seconds=diff)
    total_string = datetime.timedelta(seconds=total_diff)

    text = f'''
    Added {new_entries} after {diff_string}.\n
    Total {total_entries} after {total_string}.\n
    '''

    if new_entries < batch_size:
        log_file = 'app.log'
        last_5_lines = read_last_n_lines(log_file, 5)
        log_output = ''.join(last_5_lines)

        text = 'An error has occured!\n\n' + log_output + text

    sendMail(to, fro, text)

    if new_entries < batch_size:
        break
