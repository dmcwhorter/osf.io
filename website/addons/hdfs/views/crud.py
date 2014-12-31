# -*- coding: utf-8 -*-

import urllib
import datetime
import httplib as http

from flask import request
from modularodm import Q
from framework.exceptions import HTTPError
from framework.flask import redirect  # VOL-aware redirect
from website.models import NodeLog
from website.addons.base.views import check_file_guid
from website.project.views.node import _view_project
from website.project.views.file import get_cache_content
from website.project.decorators import (
    must_have_permission, must_be_contributor_or_public,
    must_not_be_registration, must_have_addon
)
from website.addons.hdfs.model import HdfsGuidFile
from website.addons.hdfs.settings import MAX_RENDER_SIZE
from website.addons.hdfs.api import HdfsWrapper
from website.addons.hdfs.utils import build_urls, get_cache_file_name


@must_be_contributor_or_public
@must_have_addon('hdfs', 'node')
def hdfs_download(**kwargs):

    node_settings = kwargs['node_addon']
    path = kwargs['path']

    if path is None:
        raise HTTPError(http.NOT_FOUND)
    connect = HdfsWrapper.from_addon(node_settings)
    if not connect.does_path_exist(path):
        raise HTTPError(http.NOT_FOUND)
    return connect.download_file(path)


@must_have_permission('write')
@must_not_be_registration
@must_have_addon('hdfs', 'node')
def hdfs_delete(**kwargs):

    node = kwargs['node'] or kwargs['project']
    node_settings = kwargs['node_addon']
    dfile = urllib.unquote(kwargs['path'])

    connect = HdfsWrapper.from_addon(node_settings)
    connect.delete_file(dfile)

    node.add_log(
        action='hdfs_' + NodeLog.FILE_REMOVED,
        params={
            'project': node.parent_id,
            'node': node._id,
            'path': dfile,
        },
        auth=kwargs['auth'],
        log_date=datetime.datetime.utcnow(),
    )
    return {}


@must_be_contributor_or_public
@must_have_addon('hdfs', 'node')
def hdfs_view(**kwargs):

    path = kwargs.get('path')
    vid = request.args.get('vid')
    if not path:
        raise HTTPError(http.NOT_FOUND)

    if vid == 'Pre-versioning':
        vid = 'null'

    node_settings = kwargs['node_addon']
    auth = kwargs['auth']
    node = kwargs['node'] or kwargs['project']

    wrapper = HdfsWrapper.from_addon(node_settings)
    key = wrapper.get_wrapped_key(urllib.unquote(path), vid=vid)

    if key is None:
        raise HTTPError(http.NOT_FOUND)

    try:
        guid = HdfsGuidFile.find_one(
            Q('node', 'eq', node) &
            Q('path', 'eq', path)
        )
    except:
        guid = HdfsGuidFile(
            node=node,
            path=path,
        )
        guid.save()

    redirect_url = check_file_guid(guid)
    if redirect_url:
        return redirect(redirect_url)

    cache_file_name = get_cache_file_name(path, key.etag)
    urls = build_urls(node, path, etag=key.etag)

    if key.hdfsKey.size > MAX_RENDER_SIZE:
        render = 'File too large to render; download file to view it'
    else:
        # Check to see if the file has already been rendered.
        render = get_cache_content(node_settings, cache_file_name)
        if render is None:
            file_contents = key.hdfsKey.get_contents_as_string()
            render = get_cache_content(
                node_settings,
                cache_file_name,
                start_render=True,
                remote_path=path,
                file_content=file_contents,
                download_url=urls['download'],
            )

    rv = {
        'file_name': key.name,
        'rendered': render,
        'download_url': urls['download'],
        'render_url': urls['render'],
        'info_url': urls['info'],
        'delete_url': urls['delete'],
        'files_page_url': node.web_url_for('collect_file_trees')
    }
    rv.update(_view_project(node, auth, primary=True))
    return rv


@must_be_contributor_or_public
@must_have_addon('hdfs', 'node')
def ping_render(**kwargs):
    node_settings = kwargs['node_addon']
    path = kwargs.get('path')
    etag = request.args.get('etag')

    cache_file = get_cache_file_name(path, etag)

    return get_cache_content(node_settings, cache_file)


@must_have_permission('write')
@must_not_be_registration
@must_have_addon('hdfs', 'node')
def hdfs_upload(**kwargs):

    node = kwargs['node'] or kwargs['project']
    hdfs = kwargs['node_addon']

    path = request.json.get('path', None)
    file_obj = request.files.get('file', None)
    if path is None or file_obj is None:
        raise HTTPError(http.BAD_REQUEST)

    conn = HdfsWrapper.from_addon(hdfs)
    try:
        update = conn.does_file_exist(path)
    except Exception as e:
        raise HTTPError(http.BAD_REQUEST, message=e.message)

    conn.upload_file(path, file_obj)

    node.add_log(
        action='hdfs_' +
        (NodeLog.FILE_UPDATED if update else NodeLog.FILE_ADDED),
        params={
            'project': node.parent_id,
            'node': node._primary_key,
            'path': path,
            'urls': build_urls(node, path),
        },
        auth=kwargs['auth'],
        log_date=datetime.datetime.utcnow(),
    )
    return {}


@must_be_contributor_or_public  # returns user, project
@must_have_addon('hdfs', 'node')
def file_delete_info(**kwargs):
    node = kwargs['node'] or kwargs['project']
    api_url = node.api_url
    files_page_url = node.web_url_for('collect_file_trees')
    if files_page_url is None or api_url is None:
        raise HTTPError(http.NOT_FOUND)
    return {
        'api_url': api_url,
        'files_page_url': files_page_url,
    }
