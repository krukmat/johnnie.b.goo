import random

__author__ = 'matiasleandrokruk'
import json
import subprocess
import fp
import re
import os
from fastingest import parse_json_dump


def generate_fingerprint(mp3_file):
    process = subprocess.Popen(['/home/vagrant/echoprint-codegen/echoprint-codegen', mp3_file.temporary_file_path()],
                               stderr=subprocess.STDOUT,
                               stdout=subprocess.PIPE)
    outputstring = process.communicate()[0]
    data = json.loads(outputstring)
    if data[0].get('error'):
        return data[0]['error']
    return data[0]['code']


def generate_fingerprint_from_list(results, file_list):
    # TODO: os.system is thread safe??
    codes_file = '/tmp/allcodes_%s.json' % (random.randint(1, 10000))
    command = '/home/vagrant/echoprint-codegen/echoprint-codegen -s 10 30 < %s > %s' % (file_list, codes_file)
    os.system(command)

    with open(codes_file, 'r') as data_file:
        data = json.load(data_file)
        for fingerprint in data:
            # check fp doesn't exist in database
            code_string = fingerprint['code']
            response = fp.best_match_for_query(code_string)
            if not response.match():
                label = [v for v in results if v[1] == fingerprint['metadata']['filename']][0][0]
                artist = label.split('-')[0].strip()
                title = label.split('-')[1].strip()
                fingerprint['metadata']['artist'] = artist
                fingerprint['metadata']['title'] = title
            else:
                # remove duplicate element
                data.pop(fingerprint)

    # Overwrite with artist and title
    with open(codes_file, 'w') as data_file:
        data_file.write(json.dumps(data))

    # Fastingest invoke => post all into echo-fingerprint
    codes, _ = parse_json_dump(codes_file)
    fp.ingest(codes)

    delete_file(codes_file)

    return True


def ingest(params, mp3):
    fp_code = generate_fingerprint(mp3)
    if fp_code is dict:
        return False
    if params.get('track_id', "default") == "default":
        track_id = fp.new_track_id()
    else:
        track_id = params['track_id']
    if not params.get('length', None):
        return False

    # First see if this is a compressed code
    if re.match('[A-Za-z\/\+\_\-]', fp_code) is not None:
        code_string = fp.decode_code_string(fp_code)
        if code_string is None:
            result = json.dumps({"track_id": track_id, "ok": False,
                                 "error": "cannot decode code string %s" % fp_code})
            return False, result
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


def delete_file(file):
    return os.system('sudo rm %s' % (file,))