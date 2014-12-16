# -*- coding: utf-8 -*-
from flask import request

from website.util import rubeus
from website.project.decorators import must_be_contributor_or_public, must_have_addon


def s3_hgrid_data(node_settings, auth, **kwargs):

    # Quit if no bucket
    if not node_settings.bucket or not node_settings.user_settings or not node_settings.user_settings.has_auth:
        return

    node = node_settings.owner
    return [
        rubeus.build_addon_root(
            node_settings, node_settings.bucket, permissions=auth,
            nodeUrl=node.url, nodeApiUrl=node.api_url,
        )
    ]


@must_be_contributor_or_public
@must_have_addon('s3', 'node')
def s3_dummy_folder(**kwargs):
    node_settings = kwargs['node_addon']
    auth = kwargs['auth']
    data = request.args.to_dict()
    return s3_hgrid_data(node_settings, auth, **data)
