# -*- coding: utf-8 -*-

import httplib

import itsdangerous
from flask import request

from framework.auth import Auth
from framework.sessions import Session
from framework.exceptions import HTTPError
from framework.auth.decorators import must_be_logged_in

from website import settings
from website.models import User, Node
from website.project import decorators


@decorators.must_have_permission('write')
@decorators.must_not_be_registration
def disable_addon(**kwargs):

    node = kwargs['node'] or kwargs['project']
    auth = kwargs['auth']

    addon_name = kwargs.get('addon')
    if addon_name is None:
        raise HTTPError(httplib.BAD_REQUEST)

    deleted = node.delete_addon(addon_name, auth)

    return {'deleted': deleted}


@must_be_logged_in
def get_addon_user_config(**kwargs):

    user = kwargs['auth'].user

    addon_name = kwargs.get('addon')
    if addon_name is None:
        raise HTTPError(httplib.BAD_REQUEST)

    addon = user.get_addon(addon_name)
    if addon is None:
        raise HTTPError(httplib.BAD_REQUEST)

    return addon.to_json(user)


def check_file_guid(guid):

    guid_url = '/{0}/'.format(guid._id)
    if not request.path.startswith(guid_url):
        url_split = request.url.split(guid.file_url)
        try:
            guid_url += url_split[1].lstrip('/')
        except IndexError:
            pass
        return guid_url
    return None


def get_user_from_cookie(cookie):
    token = itsdangerous.Signer(settings.SECRET_KEY).unsign(cookie)
    session = Session.load(token)
    if session is None:
        return None
    return User.load(session.data['auth_user_id'])


# TODO: Implement me
def check_token(user, token):
    pass


def get_auth(**kwargs):
    try:
        cookie = request.args['cookie']
        token = request.args['token']
        node_id = request.args['node_id']
        provider_name = request.args['provider']
    except KeyError:
        raise HTTPError(httplib.BAD_REQUEST)

    user = get_user_from_cookie(cookie)
    if user is None:
        raise HTTPError(httplib.BAD_REQUEST)

    check_token(user, token)

    node = Node.load(node_id)
    if not node:
        raise HTTPError(httplib.NOT_FOUND)

    if not node.can_view(Auth(user)):
        raise HTTPError(httplib.BAD_REQUEST)

    provider_settings = node.get_addon(provider_name)
    if not provider_settings:
        raise HTTPError(httplib.BAD_REQUEST)

    return provider_settings.serialize_credentials()
