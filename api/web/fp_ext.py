__author__ = 'matiasleandrokruk'
import logging
from fp import decode_code_string, query_fp, \
    actual_matches, get_tyrant, metadata_for_track_id
import re


def magic_matches_list(code_string, elbow=10, local=False):
    # DEC strings come in as unicode so we have to force them to ASCII
    code_string = code_string.encode("utf8")

    # First see if this is a compressed code
    if re.match('[A-Za-z\/\+\_\-]', code_string) is not None:
        code_string = decode_code_string(code_string)
        if code_string is None:
            return False

    # Query the FP flat directly.
    response = query_fp(code_string, rows=30, local=local, get_data=True)

    if len(response.results) == 0:
        return False

    # Get the actual score for all responses
    original_scores = {}
    actual_scores = {}

    trackids = [r["track_id"].encode("utf8") for r in response.results]
    tcodes = get_tyrant().multi_get(trackids)

    # For each result compute the "actual score" (based on the histogram matching)
    for (i, r) in enumerate(response.results):
        track_id = r["track_id"]
        original_scores[track_id] = int(r["score"])
        track_code = tcodes[i]
        if track_code is None:
            # Solr gave us back a track id but that track
            # is not in our keystore
            continue
        actual_scores[track_id] = actual_matches(code_string, track_code, elbow = elbow)

    # Sort the actual scores
    sorted_actual_scores = sorted(actual_scores.iteritems(), key=lambda (k,v): (v,k), reverse=True)

    # Because we split songs up into multiple parts, sometimes the results will have the same track in the
    # first few results. Remove these duplicates so that the falloff is (potentially) higher.
    final_results = []
    for trid, result in sorted_actual_scores:
        trid = trid.split("-")[0]
        meta = metadata_for_track_id(trid, local=local)
        final_results.append(meta)
    return final_results
    #return Response(Response.MULTIPLE_GOOD_MATCH_HISTOGRAM_DECREASED, TRID=trackid, score=actual_score_top_score, qtime=response.header["QTime"], tic=tic, metadata=meta)
