from djcelery.app import app

__author__ = 'matiasleandrokruk'
import requests
import youtube_dl as ydl


# TODO: Testearlo
def search_youtube_links(self, name):
    req = requests.get("http://www.youtube.com/results?", params={"search_query": "%s" % (name)})
    soup = Soup(req.text)
    links = []
    body = soup.find('ol', {'id': "search-results"})
    k = body.a
    links.append(k.get('href'))
    return "https://www.youtube.com" + links[0]

@app.task
def scrape():
    # busqueda basada en artista - track
    result = ydl.extract_info('https://www.youtube.com/watch?v=Zi_XLOBDo_Y', download=False)
    for format in result['formats']:
        if format['ext'] == 'm4a':
            url = format['url']
            r = requests.get(url, stream=True)
            chunk_size = 1000
            filename = result['display_id']+'.mp3'
            with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
            break


# for i in *mp3;do python cut_end.py ffmpeg -i $i.mp3 -ss 0:0:0 -t 0:0:30 $i.mp3;done
# crear .txt con listado
# borrar los archivos mp3 creados
# llamar tambien al bulk processor de echo-fingerprint