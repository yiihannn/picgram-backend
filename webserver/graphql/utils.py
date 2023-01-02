from graphql_relay import from_global_id
import hashlib


def parse_global_id(global_id):
    return from_global_id(global_id)[1]


def encode_file_name(file):
    readFile = file.read()
    file.seek(0)
    md5Hash = hashlib.md5(readFile)
    md5Hashed = md5Hash.hexdigest()
    return md5Hashed + ".jpg"
