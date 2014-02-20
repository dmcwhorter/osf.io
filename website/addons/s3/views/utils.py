from framework import request

from website.project.decorators import must_have_addon
from website.project.decorators import must_be_contributor_or_public

from website.addons.s3.api import create_bucket

import time
import base64
import urllib
import hmac
import sha


def generate_signed_url(mime, file_name, s3):

    expires = int(time.time() + 10)
    amz_headers = 'x-amz-acl:private'

    request_to_sign = str("PUT\n\n{mime_type}\n{expires}\n{amz_headers}\n/{resource}".format(
        mime_type=mime, expires=expires, amz_headers=amz_headers, resource=s3.bucket + '/' + file_name))

    url = 'https://s3.amazonaws.com/{bucket}/{filename}'.format(
        filename=file_name, bucket=s3.bucket)

    signed = urllib.quote_plus(base64.encodestring(
        hmac.new(str(s3.user_settings.secret_key), request_to_sign, sha).digest()).strip())

    return '{url}?AWSAccessKeyId={access_key}&Expires={expires}&Signature={signed}'.format(url=url, access_key=s3.user_settings.access_key, expires=expires, signed=signed),
    #/blackhttpmagick


@must_be_contributor_or_public
@must_have_addon('s3', 'node')
def create_new_bucket(*args, **kwargs):
    user = kwargs['auth'].user
    user_settings = user.get_addon('s3')
    if create_bucket(user_settings, request.json.get('bucket_name')):
        return {}, 200
    else:
        return {}, 400


def get_cache_file_name(key_name, etag):
    return '{0}_{1}.html'.format(key_name.replace('/', ''), etag)