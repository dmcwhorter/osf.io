import re
import sha
import hmac
import time
import base64
import urllib
import hashlib

from bson import ObjectId

from dateutil.parser import parse

from snakebite.client import Client

from website.util import rubeus

import settings as hdfs_settings


def _key_type_to_rubeus(key_type):
    if key_type == 'folder':
        return rubeus.FOLDER
    else:
        return rubeus.FILE

def serialize_obj(hdfs_wrapper):
    return [
        {
            'name': x.name,
            'path': x.path,
            'type': x.type
            }
        for x in hdfs_wrapper.get_wrapped_objects()
    ]
def build_urls(node, file_name, url=None, etag=None, vid=None):
    file_name = file_name.rstrip('/')

    rv = {
        'upload': node.api_url_for('hdfs_upload'),
        'view': node.web_url_for('hdfs_view', path=file_name),
        'delete': node.api_url_for('hdfs_delete', path=file_name),
        'info': node.api_url_for('file_delete_info', path=file_name),
        'fetch': node.api_url_for('hdfs_hgrid_data_contents', path=file_name),
        'download': u'{}{}'.format(node.api_url_for('hdfs_download', path=file_name), '' if not vid else '?vid={0}'.format(vid)),
        'render': u'{}{}'.format(node.api_url_for('ping_render', path=file_name), '' if not etag else '?etag={0}'.format(etag)),
    }

    if url:
        return rv[url]
    return rv


def get_cache_file_name(key_name, etag):
    return u'{0}_{1}.html'.format(
        hashlib.md5(key_name).hexdigest(),
        etag,
    )


def validate_base_path(name):
    validate_name = re.compile('\([^\0 !$`&*()+]\|\\\( |!|\$|`|&|\*|\(|\)|\+\)\)\+')
    return bool(validate_name.match(name))
