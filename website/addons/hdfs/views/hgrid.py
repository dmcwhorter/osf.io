# -*- coding: utf-8 -*-
import httplib as http
from urllib import unquote

from flask import request
from framework.exceptions import HTTPError
from website.util import rubeus
from website.addons.hdfs.api import HdfsWrapper, HdfsObject
from website.addons.hdfs.utils import build_urls
from website.project.decorators import must_be_contributor_or_public, must_have_addon


def hdfs_hgrid_data(node_settings, auth, **kwargs):

    # Quit if no bucket
    if not node_settings.user_settings or not node_settings.user_settings.has_auth:
        return

    node = node_settings.owner
    return [
        rubeus.build_addon_root(
            node_settings, node_settings.bucket, permissions=auth,
            nodeUrl=node.url, nodeApiUrl=node.api_url,
        )
    ]


@must_be_contributor_or_public
@must_have_addon('hdfs', 'node')
def hdfs_hgrid_data_contents(auth, node_addon, **kwargs):
    node = node_addon.owner

    path = kwargs.get('path')

    if path:
        path = unquote(path) + '/'

    can_view = node.can_view(auth)
    can_edit = node.can_edit(auth) and not node.is_registration

    hdfswrapper = HdfsWrapper.from_addon(node_addon)

    if hdfswrapper is None:
        raise HTTPError(http.BAD_REQUEST)

    def clean_name(obj):
        if path:
            return obj.name.replace(path, '')
        return obj.name

    return [
        {
            'name': clean_name(obj),
            'addon': 'hdfs',
            'permissions': {
                'edit': can_edit,
                'view': can_view
            },
            rubeus.KIND: rubeus.FILE if obj.type == 'file' else rubeus.FOLDER,
            'ext': obj.extension,
            'urls': build_urls(node, obj.name.encode('utf-8'))
        }
        for obj
        in map(HdfsObject, hdfswrapper.get_file_list(path))
        if obj.name != path
    ]


@must_be_contributor_or_public
@must_have_addon('hdfs', 'node')
def hdfs_dummy_folder(**kwargs):
    node_settings = kwargs['node_addon']
    auth = kwargs['auth']
    data = request.args.to_dict()
    return hdfs_hgrid_data(node_settings, auth, **data)
