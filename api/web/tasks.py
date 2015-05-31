import json
import urllib2

__author__ = 'matiasleandrokruk'

from celery.canvas import group
from django.conf import settings
import random

#TODO: Fix this!!! Some issue with PATH
if settings.TESTING:
    from web.utils import FingerPrintDriver, FileHandler, DiscogsDriver, YouTubeExtractor
else:
    from utils import FingerPrintDriver, FileHandler, DiscogsDriver, YouTubeExtractor

import requests
import youtube_dl
from djcelery.app import app


class StorageException(Exception):
    pass

@app.task
def discogs_scrape_artist(artist):
    track_list = DiscogsDriver.get_discogs_artist_track(artist)
    folder = 'tmp'
    # TODO: Videos as well
    files_generated = group((scrape_track.s('%s - %s' % (artist, track), folder) for track in track_list['tracklist']))
    (files_generated | generate_report.s())()
    return True

@app.task
def discogs_scrape_artists(artists):
    user_agent = 'johnnie.b.goode/1.0'
    artists_ok = []
    # TODO: Refactor into driver
    for artist in artists:
        # for every artist check if artists exists
        url = 'https://api.discogs.com/database/search?q=%s&token=%s&type=release' % (
            artist, settings.DISCOGS_PUBLIC_KEY)
        req = urllib2.Request(url, None, {'user-agent': user_agent})
        opener = urllib2.build_opener()
        f = opener.open(req)
        results = json.load(f)
        if results:
            artists_ok.append(artist)
    # checkeo que el artista exists. TODO: Optional
    group(discogs_scrape_artist.s(artist) for artist in artists)()


@app.task
def scrape_track(name, folder):
    try:
        link = YouTubeExtractor.search_youtube_links(name)
    except Exception:
        return False, False
    # search in youtube based on en artist - track
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    # Add all the available extractors
    ydl.add_default_info_extractors()
    result = ydl.extract_info(link, download=False)
    found = False
    for format in result['formats']:
        if format['ext'] == 'm4a':
            url = format['url']
            try:
                r = requests.get(url, stream=True)
                chunk_size = 1000
                filename = result['display_id']+'.mp3'
                try:
                    with open('/%s/%s' % (folder, filename,), 'wb') as fd:
                        for chunk in r.iter_content(chunk_size):
                            fd.write(chunk)
                except Exception:
                    raise StorageException('Some problem writing file /%s/%s' % (folder, filename))
                found = True
                break
            except Exception:
                pass
    if found:
        return name, '/%s/%s' % (folder, filename,)
    else:
        return False, False


@app.task(name='api.web.tasks.generate_tasks')
def generate_tasks(artist_list):
    # TODO Generate random folder
    folder = 'tmp'
    # for every list in file_list create a scrape. Do a pipe?
    files_generated = group((scrape_track.s(track, folder) for track in artist_list))
    (files_generated | generate_report.s())()
    return True


@app.task
def generate_report(results):
    random_sufix = random.randint(1, 10000)
    report_filename = '/tmp/report_%s' % (random_sufix,)
    # create summary files list
    with open(report_filename, 'wb') as fd:
        for name, _file in results:
            if name:
                fd.write("%s\n" % (_file,))
    # After all files created => call echo-fingerprint bulk process
    FingerPrintDriver.generate_fingerprint_from_list(results, report_filename)
    # delete all files in folder
    for name, _file in results:
        if name:
            FileHandler.delete_file(_file)
    # delete report file
    FileHandler.delete_file(report_filename)