__author__ = 'matiasleandrokruk'
import json
import subprocess
import fp
import re
import os


def generate_fingerprint(mp3_file):
    process = subprocess.Popen(['/home/vagrant/echoprint-codegen/echoprint-codegen', mp3_file.temporary_file_path()],
                               stderr=subprocess.STDOUT,
                               stdout=subprocess.PIPE)
    outputstring = process.communicate()[0]
    data = json.loads(outputstring)
    if data[0].get('error'):
        return data[0]['error']
    return data[0]['code']


def generate_fingerprint_from_list(file_list):
    # TODO: os.system is thread safe??
    command = '/home/vagrant/echoprint-codegen/echoprint-codegen -s 10 30 < %s > /tmp/allcodes.json' % (file_list,)
    #popen_cmd = shlex.split(command)
    #process = subprocess.Popen(popen_cmd,
    #                           stderr=subprocess.STDOUT,
    #                           stdout=subprocess.PIPE, shell=True)
    #outputstring= process.communicate('')[0]
    #print "out1 %s" % (outputstring,)
    os.system(command)
    #data = json.loads(outputstring)
    #if data[0].get('error'):
    #    return data[0]['error']
    #return data[0]['code']
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