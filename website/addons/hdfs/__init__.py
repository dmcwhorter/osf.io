from . import model
from . import routes
from . import views

MODELS = [model.AddonHdfsUserSettings, model.AddonHdfsNodeSettings, model.HdfsGuidFile]
USER_SETTINGS_MODEL = model.AddonHdfsUserSettings
NODE_SETTINGS_MODEL = model.AddonHdfsNodeSettings

ROUTES = [routes.settings_routes, routes.nonapi_routes, routes.api_routes]

SHORT_NAME = 'hdfs'
FULL_NAME = 'Hadoop Distributed Filesystem (HDFS)'

OWNERS = ['user', 'node']

ADDED_DEFAULT = []
ADDED_MANDATORY = []

VIEWS = []
CONFIGS = ['user', 'node']

CATEGORIES = ['storage']

INCLUDE_JS = {}

INCLUDE_CSS = {
    'widget': [],
    'page': [],
}

HAS_HGRID_FILES = True
GET_HGRID_DATA = views.hgrid.hdfs_hgrid_data
# 1024 ** 1024  # There really shouldnt be a limit...
MAX_FILE_SIZE = 128  # MB
