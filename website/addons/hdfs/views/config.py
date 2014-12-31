# -*- coding: utf-8 -*-

import httplib as http

from flask import request

from framework.exceptions import HTTPError
from framework.auth.decorators import must_be_logged_in

from website.project.decorators import must_have_permission
from website.project.decorators import must_not_be_registration
from website.project.decorators import must_have_addon

from website.addons.hdfs.api import has_access, HdfsParameters


def add_hdfs_auth(parameters, base_path, user_settings):

    if not has_access(parameters, base_path):
        return False

    user_settings.host = parameters.host
    user_settings.port = parameters.port
    user_settings.protocol_version = parameters.protocol_version
    user_settings.use_trash = parameters.use_trash
    user_settings.effective_user = parameters.effective_user
    user_settings.base_path = base_path

    user_settings.save()
    return True


def params_from_request(req):
    host = req.json.get('host')
    port = req.json.get('port')
    protocol_version = req.json.get('protocol_version')
    use_trash = req.json.get('use_trash')
    effective_user = req.json.get('effective_user')

    if not host or not port or not protocol_version or not use_trash or not effective_user:
        raise HTTPError(http.BAD_REQUEST)

    return HdfsParameters(host, port, protocol_version, use_trash, effective_user)


@must_be_logged_in
@must_have_addon('hdfs', 'user')
def hdfs_authorize_user(user_addon, **kwargs):

    params = params_from_request(request)
    base_path = request.json.get('base_path')

    if not add_hdfs_auth(params, base_path, user_addon):
        return {'message': 'Incorrect credentials'}, http.BAD_REQUEST

    return {}


@must_have_permission('write')
@must_have_addon('hdfs', 'node')
def hdfs_authorize_node(auth, node_addon, **kwargs):

    user = auth.user

    params = params_from_request(request)
    base_path = request.json.get('base_path')

    user_settings = user.get_addon('hdfs')
    if user_settings is None:
        user.add_addon('hdfs')
        user_settings = user.get_addon('hdfs')

    if not add_hdfs_auth(params, base_path, user_settings):
        return {'message': 'Incorrect credentials'}, http.BAD_REQUEST

    node_addon.authorize(user_settings, save=True)

    return {}


@must_have_permission('write')
@must_have_addon('hdfs', 'node')
@must_have_addon('hdfs', 'user')
def hdfs_node_import_auth(node_addon, user_addon, **kwargs):
    node_addon.authorize(user_addon, save=True)
    return {}


@must_have_permission('write')
@must_have_addon('hdfs', 'user')
@must_have_addon('hdfs', 'node')
@must_not_be_registration
def hdfs_node_settings(auth, user_addon, node_addon, **kwargs):

    user = auth.user

    # Fail if user settings not authorized
    if not user_addon.has_auth:
        raise HTTPError(http.BAD_REQUEST)

    # If authorized, only owner can change settings
    if node_addon.user_settings and node_addon.user_settings.owner != user:
        raise HTTPError(http.BAD_REQUEST)

    # Claiming the node settings
    if not node_addon.user_settings:
        node_addon.user_settings = user_addon

    return {}


@must_have_permission('write')
@must_have_addon('hdfs', 'node')
@must_not_be_registration
def hdfs_remove_node_settings(auth, node_addon, **kwargs):
    return {}


@must_be_logged_in
@must_have_addon('hdfs', 'user')
def hdfs_remove_user_settings(user_addon, **kwargs):
    return {}
