__author__ = 'matiasleandrokruk'
import json
import subprocess


def generate_fingerprint(mp3_file):
    process = subprocess.Popen(['/home/vagrant/echoprint-codegen/echoprint-codegen', mp3_file.temporary_file_path()], stderr = subprocess.STDOUT, stdout = subprocess.PIPE)
    outputstring = process.communicate()[0]
    data = json.loads(outputstring)
    return data[0]['code']