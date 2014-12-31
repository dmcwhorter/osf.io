import os

from dateutil.parser import parse

from snakebite.client import Client

from collections import namedtuple


HdfsParameters = namedtuple('HdfsParameters', 'host port protocol_version use_trash effective_user')


def connection_from_params(parameters):
    c = Client(parameters.host,
               parameters.port,
               parameters.protocol_version,
               parameters.use_trash,
               parameters.effective_user)
    return c


def has_access(parameters, path):
    return does_path_exist(parameters, path)


def create_directory(parameters, path):
    return list(connection_from_params(parameters).mkdir(path, True))


def does_path_exist(parameters, path):
    c = connection_from_params(parameters)
    return len(list(c.ls([path], include_toplevel=True, include_children=False))) > 0


class HdfsWrapper(object):

    @classmethod
    def from_addon(cls, hdfs):
        if hdfs is None or hdfs.user_settings is None:
            return None
        if not hdfs.is_registration:
            return cls(connection_from_params(HdfsParameters(hdfs.user_settings.host,
                                                             hdfs.user_settings.port,
                                                             hdfs.user_settings.protocol_version,
                                                             hdfs.user_settings.use_trash,
                                                             hdfs.user_settings.effective_user)),
                       hdfs.user_settings.base_path)
        else:
            return RegistrationWrapper(hdfs)

    "Hdfs Bucket management"

    def __init__(self, connection, base_path):
        self.connection = connection
        if not base_path.endswith('/'):
            base_path = base_path.append("/")
        self.base_path = base_path

    def get_file_list(self, prefix=None):
        if not prefix:
            return list(self.connection.ls([self.base_path], recurse=True, include_toplevel=True))
        elif not prefix.startsWith(self.base_path):
            return list(self.connection.ls(["%s%s" % self.base_path % prefix], recurse=True, include_toplevel=True))
        else:
            return list(self.connection.ls([prefix], recurse=True, include_toplevel=True))

    def check_path_includes_base(self, path):
        if not path.startswith(self.base_path):
            path = self.base_path + path
        return path

    def create_folder(self, path_to_folder=""):
        path_to_folder = self.check_path_includes_base(path_to_folder)

        return self.connection.mkdir([path_to_folder], create_parent=True)

    def delete_file(self, path_to_file, recursive=False):
        path_to_file = self.check_path_includes_base(path_to_file)
        return self.connection.delete([path_to_file], recursive)

    def upload_file(self, path_to_file, contents):
        path_to_file = self.check_path_includes_base(path_to_file)
        raise Exception("not implemented")

    def does_file_exist(self, path_to_file):
        path_to_file = self.check_path_includes_base(path_to_file)
        if self.connection.test([path_to_file], directory=True):
            raise Exception("There is a directory at the specified path %s" % path_to_file)
        return self.connection.test([path_to_file], exists=True)

    def download_file(self, path_to_file):
        # headers = {'response-content-disposition': 'attachment'}
        path_to_file = self.check_path_includes_base(path_to_file)
        return iter(self.connection.cat([path_to_file], check_crc=True)).next()  # TODO: check for invalid path

    def get_wrapped_objects(self, prefix=None):
        return [HdfsObject(x) for x in self.get_file_list(prefix)]

    def get_wrapped_files_in_dir(self, directory=None):
        return [HdfsObject(x) for x in self.get_file_list(directory) if x['file_type'] == 'f']

    def get_wrapped_directories_in_dir(self, directory=None):
        return [HdfsObject(x) for x in self.get_file_list(directory) if x['file_type'] == 'd']


# TODO Add null checks etc
class RegistrationWrapper(HdfsWrapper):

    def __init__(self, node_settings):
        if node_settings.user_settings:
            connection = connection_from_params(HdfsParameters(
                node_settings.user_settings.host,
                node_settings.user_settings.port,
                node_settings.user_settings.protocol_version,
                node_settings.user_settings.use_trash,
                node_settings.user_settings.effective_user
            ))
        else:
            connection = connection_from_params(HdfsParameters())  # TODO: this is unlikely to work, handle better
        base_path = node_settings.user_settings.base_path
        super(RegistrationWrapper, self).__init__(connection, base_path)
        self.registration_data = node_settings.registration_data


class HdfsObject(object):

    def __init__(self, dictionary):
        self.dictionary = dictionary

    @property
    def path(self):
        return self.dictionary['path']

    @property
    def name(self):
        d = self.path.split('/')
        if len(d) > 1 and self.type == 'file':
            return d[-1]
        elif self.type == 'folder':
            return d[-2]
        else:
            return d[0]

    @property
    def type(self):
        if self.dictionary['file_type'] == 'f':
            return 'file'
        elif self.dictionary['file_type'] == 'd':
            return 'folder'
        else:
            raise Exception("unexpected file type")  # TODO: more specific type of exception?

    @property
    def parent_folder(self):
        d = self.path.split('/')

        if len(d) > 1 and self.type == 'file':
            return d[len(d) - 2]
        elif len(d) > 2 and self.type == 'folder':
            return d[len(d) - 3]
        else:
            return None

    @property
    def size(self):
        if self.type == 'folder':
            return None
        else:
            return long(self.dictionary['length'])

    @property
    def last_mod(self):
        if self.type == 'folder':
            return None
        else:
            return parse(self.dictionary['modification_time'])


    @property
    def extension(self):
        if self.type != 'folder':
            if os.path.splitext(self.path)[1] is None:
                return None
            else:
                return os.path.splitext(self.path)[1][1:]
        else:
            return None
