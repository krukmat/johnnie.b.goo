import json
import sys
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

sys.path.append('/home/vagrant/echoprint-server/API')
import fp
import re
from utils import *

# Create your views here.


@csrf_exempt
def ingest(request):
    params = request.POST
    mp3 = request.FILES['mp3']
    # TODO: Convert music -> fingerprint code
    fp_code = generate_fingerprint(mp3)
    if fp_code is dict:
        return HttpResponse(fp_code['error'], status=400)
    if params['track_id'] == "default":
        track_id = fp.new_track_id()
    else:
        track_id = params.track_id
    if params['length'] is None:
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
        data["artist"] = params.artist
    if params.get('release'):
        data["release"] = params.release
    if params.get('track'):
        data["track"] = params.track
    fp.ingest(data, do_commit=True, local=False)

    data = json.dumps({"track_id": track_id, "fp": fp_code,"status": "ok"})
    return HttpResponse(data, status=200)


@csrf_exempt
def query(request):
    mp3 = request.FILES['mp3']
    # TODO: Convert music -> fingerprint code
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