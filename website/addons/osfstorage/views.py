#!/usr/bin/env python
# encoding: utf-8

import httplib
import logging

from flask import request

from framework.flask import redirect
from framework.exceptions import HTTPError
from framework.analytics import update_counter

from website.models import User
from website.project.decorators import (
    must_be_contributor, must_be_contributor_or_public,
    must_have_permission, must_not_be_registration, must_have_addon,
)
from website.util import rubeus
from website.project.utils import serialize_node
from website.addons.base.views import check_file_guid

from website.addons.osfstorage import model
from website.addons.osfstorage import utils
from website.addons.osfstorage import errors
from website.addons.osfstorage import settings as osf_storage_settings


logger = logging.getLogger(__name__)

MEGABYTE = 1024 * 1024


def make_error(code, message_short=None, message_long=None):
    data = {}
    if message_short:
        data['message_short'] = message_short
    if message_long:
        data['message_long'] = message_long
    return HTTPError(code, data=data)


def get_record_or_404(path, node_addon, touch=True):
    record = model.OsfStorageFileRecord.find_by_path(path, node_addon, touch=touch)
    if record is not None:
        return record
    raise HTTPError(httplib.NOT_FOUND)


def osf_storage_crud_prepare(path, node_addon):
    record = model.OsfStorageFileRecord.find_by_path(path, node_addon)
    if record is None:
        raise HTTPError(httplib.NOT_FOUND)
    try:
        auth = request.json['auth']
        location = request.json['location']
        metadata = request.json['metadata']
    except KeyError:
        raise HTTPError(httplib.BAD_REQUEST)
    user = User.load(auth.get('uid'))
    if user is None:
        raise HTTPError(httplib.BAD_REQUEST)
    return user, record, location, metadata


def osf_storage_crud_hook_post(path, node_addon, **kwargs):
    user, record, location, metadata = osf_storage_crud_prepare(path, node_addon)
    record.create_version(user, location, metadata)
    return {'status': 'success'}


def osf_storage_crud_hook_put(path, node_addon, **kwargs):
    user, record, location, metadata = osf_storage_crud_prepare(path, node_addon)
    record.update_version_metadata(user, location, metadata)
    return {'status': 'success'}


def parse_version_specifier(version_str):
    """
    :raise: `InvalidVersionError` if version specifier cannot be parsed
    """
    try:
        version_idx = int(version_str)
    except (TypeError, ValueError):
        raise errors.InvalidVersionError
    if version_idx < 1:
        raise errors.InvalidVersionError
    return version_idx


def get_version_helper(file_record, version_str):
    """
    :return: Tuple of (version_index, file_version); note that index is one-based
    :raise: `HTTPError` if version specifier is invalid or version not found
    """
    if version_str is None:
        return (
            len(file_record.versions),
            file_record.versions[-1],
        )
    try:
        version_idx = parse_version_specifier(version_str)
    except errors.InvalidVersionError:
        raise make_error(httplib.BAD_REQUEST, 'Invalid version')
    try:
        return version_idx, file_record.versions[version_idx - 1]
    except IndexError:
        raise HTTPError(httplib.NOT_FOUND)


def get_version(path, node_settings, version_str, throw=True):
    """Resolve version from request arguments.

    :param str path: Path to file
    :param node_settings: Node settings record
    :param str version_str: Version from query string
    :param bool throw: Throw `HTTPError` if version is incomplete
    :return: Tuple of (<one-based version index>, <file version>, <file record>)
    """
    record = model.OsfStorageFileRecord.find_by_path(path, node_settings)
    if record is None:
        raise HTTPError(httplib.NOT_FOUND)
    if record.is_deleted:
        raise HTTPError(httplib.GONE)
    version_idx, file_version = get_version_helper(record, version_str)
    return version_idx, file_version, record


def serialize_file(idx, version, record, path, node):
    """Serialize data used to render a file.
    """
    rendered = utils.render_file(idx, version, record)
    return {
        'file_name': record.name,
        'file_revision': 'Version {0}'.format(idx),
        'file_path': record.path,
        'rendered': rendered,
        'files_url': node.web_url_for('collect_file_trees'),
        'download_url': node.web_url_for('osf_storage_view_file', path=path, action='download'),
        'delete_url': node.api_url_for('osf_storage_delete_file', path=path),
        'revisions_url': node.api_url_for(
            'osf_storage_get_revisions',
            path=path,
        ),
        'render_url': node.api_url_for(
            'osf_storage_render_file',
            path=path,
            version=idx,
        ),
    }


def download_file(path, node_addon, version_query):
    mode = request.args.get('mode')
    idx, version, record = get_version(path, node_addon, version_query)
    url = utils.get_download_url(record, version)
    if mode != 'render':
        update_analytics(node_addon.owner, path, idx)
    return redirect(url)


def view_file(auth, path, node_addon, version_query):
    node = node_addon.owner
    idx, version, record = get_version(path, node_addon, version_query, throw=False)
    file_obj = model.OsfStorageGuidFile.get_or_create(node=node, path=path)
    redirect_url = check_file_guid(file_obj)
    if redirect_url:
        return redirect(redirect_url)
    ret = serialize_file(idx, version, record, path, node)
    ret.update(serialize_node(node, auth, primary=True))
    return ret


@must_be_contributor_or_public
@must_have_addon('osfstorage', 'node')
def osf_storage_view_file(auth, path, node_addon, **kwargs):
    action = request.args.get('action', 'view')
    version_idx = request.args.get('version')
    if action == 'download':
        return download_file(path, node_addon, version_idx)
    if action == 'view':
        return view_file(auth, path, node_addon, version_idx)
    raise HTTPError(httplib.BAD_REQUEST)


def update_analytics(node, path, version_idx):
    """
    :param Node node: Root node to update
    :param str path: Path to file
    :param int version_idx: One-based version index
    """
    update_counter(u'download:{0}:{1}'.format(node._id, path))
    update_counter(u'download:{0}:{1}:{2}'.format(node._id, path, version_idx))


@must_be_contributor_or_public
@must_have_addon('osfstorage', 'node')
def osf_storage_render_file(path, node_addon, **kwargs):
    version = request.args.get('version')
    idx, version, record = get_version(path, node_addon, version)
    return utils.render_file(idx, version, record)


@must_be_contributor
@must_not_be_registration
@must_have_permission('write')
@must_have_addon('osfstorage', 'node')
def osf_storage_delete_file(auth, path, node_addon, **kwargs):
    file_record = model.OsfStorageFileRecord.find_by_path(path, node_addon)
    if file_record is None:
        raise HTTPError(httplib.NOT_FOUND)
    try:
        file_record.delete(auth)
    except errors.DeleteError:
        raise HTTPError(httplib.NOT_FOUND)
    file_record.save()
    return {'status': 'success'}


@must_be_contributor_or_public
@must_have_addon('osfstorage', 'node')
def osf_storage_hgrid_contents(auth, node_addon, **kwargs):
    path = kwargs.get('path', '')
    file_tree = model.OsfStorageFileTree.find_by_path(path, node_addon)
    if file_tree is None:
        if path == '':
            return []
        raise HTTPError(httplib.NOT_FOUND)
    node = node_addon.owner
    permissions = utils.get_permissions(auth, node)
    return [
        utils.serialize_metadata_hgrid(item, node, permissions)
        for item in list(file_tree.children)
        if item.touch() and not item.is_deleted
    ]


def osf_storage_root(node_settings, auth, **kwargs):
    """Build HGrid JSON for root node. Note: include node URLs for client-side
    URL creation for uploaded files.
    """
    node = node_settings.owner
    root = rubeus.build_addon_root(
        node_settings=node_settings,
        name='',
        permissions=auth,
        nodeUrl=node.url,
        nodeApiUrl=node.api_url,
    )
    return [root]


@must_be_contributor_or_public
@must_have_addon('osfstorage', 'node')
def osf_storage_get_revisions(path, node_addon, **kwargs):
    node = node_addon.owner
    page = request.args.get('page', 0)
    try:
        page = int(page)
    except (TypeError, ValueError):
        raise HTTPError(httplib.BAD_REQUEST)
    record = model.OsfStorageFileRecord.find_by_path(path, node_addon)
    if record is None:
        raise HTTPError(httplib.NOT_FOUND)
    indices, versions, more = record.get_versions(
        page,
        size=osf_storage_settings.REVISIONS_PAGE_SIZE,
    )
    return {
        'revisions': [
            utils.serialize_revision(node, record, versions[idx], indices[idx])
            for idx in range(len(versions))
        ],
        'more': more,
    }


@must_be_contributor_or_public
@must_have_addon('osfstorage', 'node')
def osf_storage_view_file_legacy(fid, node_addon, **kwargs):
    node = node_addon.owner
    return redirect(
        node.web_url_for(
            'osf_storage_view_file',
            path=fid,
        ),
        code=httplib.MOVED_PERMANENTLY,
    )


@must_be_contributor_or_public
@must_have_addon('osfstorage', 'node')
def osf_storage_download_file_legacy(fid, node_addon, **kwargs):
    node = node_addon.owner
    version = kwargs.get('vid', None)
    return redirect(
        node.web_url_for(
            'osf_storage_view_file',
            path=fid,
            version=version,
            action='download',
        ),
        code=httplib.MOVED_PERMANENTLY,
    )
