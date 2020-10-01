#! /usr/bin/env python3
#! /usr/bin/env ipython3 -i

from lyricsgenius import Genius
import os
import json
import re
from collections import Counter
import snowballstemmer
from wordfreq import word_frequency

def get_lyrics(interpret):
    if not os.path.exists(f"Lyrics_{interpret}.json"):
        with open("token", "r") as f:
            token = f.read().strip()

        genius = Genius(token)
        artist = genius.search_artist(interpret)
        artist.save_lyrics()
    with open(f"Lyrics_{interpret}.json", "r") as f:
        lyrics = json.loads(f.read())
    return lyrics

def clean_lyrics(lyrics):
    all_lyrics = ""
    for song in lyrics["songs"]:
        if not "(Promo)" in song["title"]:
            all_lyrics += "\n" + song["lyrics"]
    return all_lyrics[1:]

def add_to_artist(la, r, prev, artists):
    seg = lyrics[prev.end():r.start() if r else -1]
    match = False
    x = re.search(r"[1-9]x", seg)
    times = 1
    if x is not None:
        seg = seg.replace(x.group(), "")
        times = int(x.group()[0])
    else:
        x = re.search(r"x[1-9]", seg)
        if x is not None:
            seg = seg.replace(x.group(), "")
            times = int(x.group()[1])
    for artist in artists:
        if artist in prev.group():
            la[artist] += times*("\n" + seg)
            match = True
    if not match:
        la["misc"] += times*("\n" + seg)

def clean2(lyrics):
    lyrics = lyrics.replace("K.I.Z.", "kiz")
    for c in ":.,„”!?()\"-*\n{}&–":
        lyrics = lyrics.replace(c, " ")
    lyrics = lyrics.replace("'", "")
    lyrics = lyrics.lower()
    lyrics = re.sub(r"\s+", " ", lyrics)
    words = lyrics.split()
    #  stemmer = snowballstemmer.stemmer("german")
    #  words = stemmer.stemWords(words)
    return words

def filter_for_artists(lyrics, *artists):
    res = re.finditer(r"\[.*\]", lyrics)
    prev = None
    la = {artist: "" for artist in artists}
    la["misc"] = ""
    for r in res:
        if not prev is None:
            add_to_artist(la, r, prev, artists)
        prev = r
    add_to_artist(la, None, prev, artists)
    return {key: clean2(val) for key, val in la.items()}

def get_weighted_freq(w, l):
    w, c = w
    f = c/l
    fr = word_frequency(w, 'de', 'small')
    if fr == 0:
        fr = 1
    f /= fr
    return (w, f, c)

def count(words):
    l = len(words)
    count = Counter(words)
    freq = list(map(lambda w: get_weighted_freq(w, l), count.items()))
    freq = sorted(freq, key=lambda x: x[1], reverse=True)
    return freq

if __name__ == '__main__':
    lyrics = get_lyrics("K.I.Z.")
    lyrics = clean_lyrics(lyrics)
    la = filter_for_artists(lyrics, "Tarek", "Maxim", "Nico")

    freq_tarek = count(la["Tarek"])
    freq_nico = count(la["Nico"])
    freq_maxim = count(la["Maxim"])
    freq_misc = count(la["misc"])
    with open("KIZ.md", "w") as f:
        f.write("| Tarek | Nico | Maxim | Misc |\n")
        f.write("|---|---|---|---|\n")
        N = 100
        for tf, nf, mf, xf in zip(freq_tarek[:N], freq_nico[:N],
                freq_maxim[:N], freq_misc[:N]):
            f.write(f"| {tf[0]} ({tf[2]}) | {nf[0]} ({nf[2]}) | {mf[0]}" +
                    f" ({mf[2]}) | {xf[0]} ({xf[2]}) |\n")

    freq_tarek = sorted(freq_tarek, key=lambda x: x[2], reverse=True)
    freq_nico = sorted(freq_nico, key=lambda x: x[2], reverse=True)
    freq_maxim = sorted(freq_maxim, key=lambda x: x[2], reverse=True)
    freq_misc = sorted(freq_misc, key=lambda x: x[2], reverse=True)
    with open("KIZ2.md", "w") as f:
        f.write("| Tarek | Nico | Maxim | Misc |\n")
        f.write("|---|---|---|---|\n")
        N = 100
        for tf, nf, mf, xf in zip(freq_tarek[:N], freq_nico[:N],
                freq_maxim[:N], freq_misc[:N]):
            f.write(f"| {tf[0]} ({tf[2]}) | {nf[0]} ({nf[2]}) | {mf[0]}" +
                    f" ({mf[2]}) | {xf[0]} ({xf[2]}) |\n")

