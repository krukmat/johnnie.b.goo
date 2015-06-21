import json
import urllib2

__author__ = 'matiasleandrokruk'

from celery.canvas import group
from django.conf import settings
import random

# TODO: Fix this!!! Some issue with PATH
if settings.TESTING:
    from web.utils import FingerPrintDriver, FileHandler, DiscogsDriver, YouTubeExtractor, chunks
else:
    from utils import FingerPrintDriver, FileHandler, DiscogsDriver, YouTubeExtractor, chunks
import requests
import youtube_dl
from djcelery.app import app
from models import Track

class StorageException(Exception):
    pass

@app.task
def scrape_track(name, folder):
    # TODO DETAIL in log
    name_parts = name.split('-')
    if len(name_parts) == 4:
        year = name_parts[0]
        title = name_parts[1]
        artist = name_parts[2]
        track = name_parts[3]
    else:
        print "Invalid name: %s" % (name,)
        return False, False

    track_name = '%s - %s' % (artist, track)
    try:
        link = YouTubeExtractor.search_youtube_links(track_name)
    except Exception:
        return False, False
    try:
        # search in youtube based on en artist - track
        ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        # Add all the available extractors
        ydl.add_default_info_extractors()
        result = ydl.extract_info(link, download=False)
        found = False
        Track.sync()
        display_id = result['display_id']
        exists = Track.objects.filter(youtube_code=display_id).count() > 0
        # Check Tracker.youtube_code doesn't exist
        if not exists:
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
        else:
            return False, False
    except:
        return False, False


@app.task(name='api.web.tasks.generate_tracks_import')
def generate_tracks_import(tracks_list):
    # TODO Generate random folder
    folder = 'tmp'
    print tracks_list
    # for every list in file_list create a scrape. Do a pipe?
    files_generated = group((scrape_track.s(track, folder) for track in tracks_list))
    (files_generated | generate_report.s())()
    return True


@app.task
def generate_report(results):
    # TODO DETAIL in log (use logger instead of print)
    if results and len(results) > 0:
        print results
        random_sufix = random.randint(1, 10000)
        report_filename = '/tmp/report_%s' % (random_sufix,)
        # create summary files list
        with open(report_filename, 'wb') as fd:
            results_refined = [result for result in results if isinstance(result, (list, tuple))]
            try:
                for name, _file in results_refined:
                    if name:
                        fd.write("%s\n" % (_file,))
            except TypeError:
                pass
        # After all files created => call echo-fingerprint bulk process
        FingerPrintDriver.generate_fingerprint_from_list(results, report_filename)
        # delete all files in folder
        for name, _file in results:
            if name:
                print "%s:%s was added to the database" % (name, _file)
                FileHandler.delete_file(_file)
        # delete report file
        FileHandler.delete_file(report_filename)


@app.task
def discogs_scrape_artist(artist, limit=None):
    # TODO DETAIL in log
    # TODO: Filter better. Check discogs attributes to refining track's list.
    track_list = DiscogsDriver.get_discogs_artist_track(artist)
    if limit:
        track_list_slice = track_list['tracks'][:limit]
    else:
        track_list_slice = track_list['tracks']
    for sub_list in list(chunks(track_list_slice, 10)):
        generate_tracks_import.delay(sub_list)
    return True

@app.task(name='api.web.tasks.discogs_scrape_artists')
def discogs_scrape_artists(artists):
    # TODO DETAIL in log
    print artists
    artists_ok = DiscogsDriver.get_valid_artists(artists)
    print artists_ok
    for artist, name in artists_ok:
        print "scrapping %s" % (name,)
        discogs_scrape_artist.delay(artist)