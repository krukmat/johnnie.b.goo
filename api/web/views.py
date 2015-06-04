import StringIO
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import fp
from api.web.tasks import generate_tracks_import, discogs_scrape_artists
from utils import *

# Create your views here.


@csrf_exempt
def ingest(request):
    params = request.POST
    mp3 = request.FILES['mp3']
    fp_code = generate_fingerprint(mp3)
    if fp_code is dict:
        return HttpResponse(fp_code['error'], status=400)
    if params.get('track_id', "default") == "default":
        track_id = fp.new_track_id()
    else:
        track_id = params['track_id']
    if not params.get('length', None):
        return HttpResponse("Invalid data", status=400)

    # First see if this is a compressed code
    if re.match('[A-Za-z\/\+\_\-]', fp_code) is not None:
        code_string = fp.decode_code_string(fp_code)
        if code_string is None:
            result = json.dumps( {"track_id": track_id, "ok": False,
                                  "error": "cannot decode code string %s" % fp_code})
            return HttpResponse(result, status=400)
    else:
        code_string = fp_code

    data = {"track_id": track_id,
            "fp": code_string,
            "length": params['length'],
            "codever": params['codever']}
    if params.get('artist'):
        data["artist"] = params.get('artist')
    if params.get('release'):
        data["release"] = params.get('release')
    if params.get('track'):
        data["track"] = params.get('track')
    fp.ingest(data, do_commit=True, local=False)

    data = json.dumps({"track_id": track_id, "fp": fp_code,"status": "ok"})
    return HttpResponse(data, status=200)


@csrf_exempt
def query(request):
    mp3 = request.FILES['mp3']
    # Convert music -> fingerprint code
    fp_code = generate_fingerprint(mp3)
    if fp_code is dict:
        return HttpResponse(fp_code['error'], status=400)
    # First see if this is a compressed code
    if re.match('[A-Za-z\/\+\_\-]', fp_code) is not None:
        code_string = fp.decode_code_string(fp_code)
        if code_string is None:
            result = json.dumps({"error": "cannot decode code string %s" % fp_code})
            return HttpResponse(result, status=400)
    else:
        code_string = fp_code

    response = fp.best_match_for_query(code_string)
    metadata = response.metadata
    if metadata:
        metadata.pop('import_date')
    data = json.dumps({"ok": True, "message": response.message(), "match": response.match(),
                       "score": response.score, \
                       "qtime": response.qtime, "track_id": response.TRID,
                       "total_time": response.total_time,
                       "metadata": metadata})
    return HttpResponse(data, status=200)


@csrf_exempt
def bulk_process(request):
    file_list = request.FILES['list_file']
    discogs_check = request.POST.get('discogs', True)
    artists_list = []
    for line in file_list:
        artists_list.append(line)
    if artists_list:
        if discogs_check:
            discogs_scrape_artists.delay(artists_list)
        else:
            generate_tracks_import.delay(artists_list)
    return HttpResponse('OK', status=200)