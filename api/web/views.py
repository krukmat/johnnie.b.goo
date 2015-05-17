import json
import sys
from django.http.response import HttpResponse

sys.path.append('/home/vagrant/echoprint-server/API')
import fp
import re

# Create your views here.


def ingest(request):
    params = request.POST
    # TODO: Convert music -> fingerprint code
    if params['track_id'] == "default":
        track_id = fp.new_track_id()
    else:
        track_id = params.track_id
    if params['length'] is None or params['codever'] is None:
        return HttpResponse("Invalid data", status=400)

    # First see if this is a compressed code
    if re.match('[A-Za-z\/\+\_\-]', params['fp_code']) is not None:
        code_string = fp.decode_code_string(params['fp_code'])
        if code_string is None:
            result = json.dumps( {"track_id": track_id, "ok": False,
                                "error": "cannot decode code string %s" % params['fp_code']})
            return HttpResponse(result, status=400)
    else:
        code_string = params['fp_code']

    data = {"track_id": track_id,
            "fp": code_string,
            "length": params.length,
            "codever": params.codever}
    if params['artist']:
        data["artist"] = params.artist
    if params['release']:
        data["release"] = params.release
    if params['track']:
        data["track"] = params.track
    fp.ingest(data, do_commit=True, local=False)

    return json.dumps({"track_id": track_id, "status": "ok"})


def query(request):
    fp_code = request.GET['fp_code']
    response = fp.best_match_for_query(fp_code)
    data = json.dumps({"ok": True, "query": fp_code, "message": response.message(), "match": response.match(),
                       "score": response.score, \
                       "qtime": response.qtime, "track_id": response.TRID, "total_time": response.total_time})
    return HttpResponse(data, status=200)