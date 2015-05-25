__author__ = 'matiasleandrokruk'

from celery.canvas import group
import random
from utils import generate_fingerprint_from_list, delete_file
import requests
import youtube_dl
from bs4 import BeautifulSoup
from djcelery.app import app


def search_youtube_links(name):
    req = requests.get("http://www.youtube.com/results?", params={"search_query": "%s" % (name)})
    soup = BeautifulSoup(req.text)
    links = []
    body = soup.find('div', {'id': "results"})
    li = body.find('ol').find('ol').find('li')
    k = li.find('h3', {'class': 'yt-lockup-title'}).find('a')
    links.append(k.get('href'))
    return "https://www.youtube.com" + links[0]


@app.task
def scrape(name, folder):
    link = search_youtube_links(name)
    # busqueda basada en artista - track
    ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    # Add all the available extractors
    ydl.add_default_info_extractors()
    result = ydl.extract_info(link, download=False)
    for format in result['formats']:
        if format['ext'] == 'm4a':
            url = format['url']
            r = requests.get(url, stream=True)
            chunk_size = 1000
            filename = result['display_id']+'.mp3'
            with open('/%s/%s' % (folder, filename,), 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            break
    return name, '/%s/%s' % (folder, filename,)


@app.task
def generate_tasks(file_list):
    # Generate random folder
    folder = 'tmp'
    # for every list in file_list create a scrape. Do a pipe?
    files_generated = group((scrape.s(track, folder) for track in file_list))
    (files_generated | generate_report.s())()
    return True


@app.task
def generate_report(results):
    random_sufix = random.randint(1, 10000)
    report_filename = '/tmp/report_%s' % (random_sufix,)
    # create summary files list
    with open(report_filename, 'wb') as fd:
        for name, _file in results:
            fd.write("%s\n" % (_file,))
    # After all files created => call echo-fingerprint bulk process
    generate_fingerprint_from_list(report_filename)
    # TODO: Import allcodes.json. Missing metadata (artist, track)
    # delete all files in folder
    for name, _file in results:
        delete_file(_file)
    # delete report file
    delete_file(report_filename)




# for i in *mp3;do python cut_end.py ffmpeg -i $i.mp3 -ss 0:0:0 -t 0:0:30 $i.mp3;done
# crear .txt con listado
# borrar los archivos mp3 creados
# llamar tambien al bulk processor de echo-fingerprint