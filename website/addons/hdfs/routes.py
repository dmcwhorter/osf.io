from framework.routing import Rule, json_renderer
from website.routes import OsfWebRenderer
from website.addons.hdfs import views

settings_routes = {
    'rules': [
        Rule(
            '/settings/hdfs/',
            'post',
            views.config.hdfs_authorize_user,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/settings/',
                '/project/<pid>/node/<nid>/hdfs/settings/',
            ],
            'post',
            views.config.hdfs_node_settings,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/settings/',
                '/project/<pid>/node/<nid>/hdfs/settings/',
                '/project/<pid>/hdfs/config/',
                '/project/<pid>/node/<nid>/hdfs/config/',
            ],
            'delete',
            views.config.hdfs_remove_node_settings,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/import-auth/',
                '/project/<pid>/node/<nid>/hdfs/import-auth/',
            ],
            'post',
            views.config.hdfs_node_import_auth,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/authorize/',
                '/project/<pid>/node/<nid>/hdfs/authorize/',
            ],
            'post',
            views.config.hdfs_authorize_node,
            json_renderer
        ),
        Rule(
            '/settings/hdfs/',
            'delete',
            views.config.hdfs_remove_user_settings,
            json_renderer
        ),
    ],
    'prefix': '/api/v1',
}

api_routes = {
    'rules': [
        Rule(
            [
                '/project/<pid>/hdfs/',
                '/project/<pid>/node/<nid>/hdfs/'
            ],
            'post',
            views.crud.hdfs_upload,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/<path:path>/',
                '/project/<pid>/node/<nid>/hdfs/<path:path>/',
            ],
            'delete',
            views.crud.hdfs_delete,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/<path:path>/render/',
                '/project/<pid>/node/<nid>/hdfs/<path:path>/render/',
            ],
            'get',
            views.crud.ping_render,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/hgrid/',
                '/project/<pid>/node/<nid>/hdfs/hgrid/',
                '/project/<pid>/hdfs/hgrid/<path:path>/',
                '/project/<pid>/node/<nid>/hdfs/hgrid/<path:path>/',
            ],
            'get',
            views.hgrid.hdfs_hgrid_data_contents,
            json_renderer
        ),
        Rule(
            [
                '/project/<pid>/hdfs/hgrid/dummy/',
                '/project/<pid>/node/<nid>/hdfs/hgrid/dummy/',
            ],
            'get',
            views.hgrid.hdfs_dummy_folder,
            json_renderer,
        ),
        Rule(
            [
                '/project/<pid>/hdfs/<path:path>/info/',
                '/project/<pid>/node/<nid>/hdfs/<path:path>/info/',
            ],
            'get',
            views.crud.file_delete_info,
            json_renderer
        ),
    ],
    'prefix': '/api/v1',
}


nonapi_routes = {
    'rules': [
        Rule(
            [
                '/project/<pid>/hdfs/<path:path>/',
                '/project/<pid>/node/<nid>/hdfs/<path:path>/'
            ],
            'get',
            views.crud.hdfs_view,
            OsfWebRenderer('../addons/hdfs/templates/hdfs_view_file.mako')
        ),
        Rule(
            [
                '/project/<pid>/hdfs/<path:path>/download/',
                '/project/<pid>/node/<nid>/hdfs/<path:path>/download/'
            ],
            'get',
            views.crud.hdfs_download,
            json_renderer
        ),
    ]
}
