'''
Created on Jan 7, 2014

@author: seto
'''
"""

"""

import os

from modularodm import fields

from framework.auth.core import Auth

from website.addons.base import AddonUserSettingsBase, AddonNodeSettingsBase, GuidFile
from website.addons.hdfs.api import HdfsWrapper, has_access
from website.addons.hdfs.utils import serialize_obj


class HdfsGuidFile(GuidFile):

    path = fields.StringField(index=True)

    @property
    def file_url(self):
        if self.path is None:
            raise ValueError('Path field must be defined.')
        return os.path.join('hdfs', self.path)


class AddonHdfsUserSettings(AddonUserSettingsBase):

    hdfs_host = fields.StringField()
    hdfs_port = fields.IntegerField()
    hdfs_protocol_version = fields.IntegerField()
    hdfs_use_trash = fields.BooleanField()
    hdfs_base_path = fields.StringField()
    hdfs_effective_user = fields.StringField()

    def to_json(self, user):
        rv = super(AddonHdfsUserSettings, self).to_json(user)
        rv['has_auth'] = self.has_auth
        return rv

    @property
    def has_auth(self):
        return bool(self.hdfs_host and self.hdfs_port and self.hdfs_protocol_version and self.hdfs_use_trash and
                    self.hdfs_effective_user and self.hdfs_base_path)


class AddonHdfsNodeSettings(AddonNodeSettingsBase):

    registration_data = fields.DictionaryField()
    user_settings = fields.ForeignField(
        'addonhdfsusersettings', backref='authorized'
    )
    node_path = fields.StringField()  # relative to base_path

    @property
    def user_has_auth(self):
        return self.user_settings.has_auth

    @property
    def node_has_auth(self):
        return True if self.node_path else False

    @property
    def is_registration(self):
        return True if self.registration_data else False

    def after_register(self, node, registration, user, save=True):
        """

        :param Node node: Original node
        :param Node registration: Registered node
        :param User user: User creating registration
        :param bool save: Save settings after callback
        :return tuple: Tuple of cloned settings and alert message

        """

        clone, message = super(AddonHdfsNodeSettings, self).after_register(
            node, registration, user, save=False
        )

        clone.user_settings = self.user_settings
        clone.registration_data['objects'] = serialize_obj(HdfsWrapper.from_addon(self))

        if save:
            clone.save()

        return clone, message

    def before_register(self, node, user):
        """

        :param Node node:
        :param User user:
        :return str: Alert message

        """
        if self.user_settings and self.user_settings.has_auth:
            wrapper = HdfsWrapper.from_addon(self)
            has_access(wrapper.params, self.node_path)

            return (
                'Registering {cat} "{title}" will copy the node path for its '
                'HDFS add-on to the registered {cat}. '
                # 'As well as turning versioning on in your bucket,'
                # 'which may result in larger charges from Amazon'
            ).format(
                cat=node.project_or_component,
                title=node.title,
                node_path=self.node_path
            )

    def after_fork(self, node, fork, user, save=True):
        """

        :param Node node: Original node
        :param Node fork: Forked node
        :param User user: User creating fork
        :param bool save: Save settings after callback
        :return tuple: Tuple of cloned settings and alert message

        """
        clone, _ = super(AddonHdfsNodeSettings, self).after_fork(
            node, fork, user, save=False
        )

        # Copy authentication if authenticated by forking user
        if self.user_settings and self.user_settings.owner == user:
            clone.user_settings = self.user_settings
            clone.node_path = self.node_path
            message = (
                'HDFS node path copied to forked {cat}.'
            ).format(
                cat=fork.project_or_component,
            )
        else:
            message = (
                'HDFS node path not copied to forked {cat}. You may '
                'authorize this fork on the <a href={url}>Settings</a> '
                'page.'
            ).format(
                cat=fork.project_or_component,
                url=fork.url + 'settings/'
            )

        if save:
            clone.save()

        return clone, message

    def before_fork(self, node, user):
        """

        :param Node node:
        :param User user:
        :return str: Alert message

        """

        if self.user_settings and self.user_settings.owner == user:
            return (
                'Because you have authenticated the Hdfs add-on for this '
                '{cat}, forking it will also transfer the node path to '
                'the forked {cat}.'
            ).format(
                cat=node.project_or_component,
            )
        return (
            'Because this Hdfs add-on has been authenticated by a different '
            'user, forking it will not transfer the node path to the forked '
            '{cat}.'
        ).format(
            cat=node.project_or_component,
        )

    def before_remove_contributor(self, node, removed):
        """

        :param Node node:
        :param User removed:
        :return str: Alert message

        """
        if self.user_settings and self.user_settings.owner == removed:
            return (
                'The HDFS add-on for this {category} is authenticated '
                'by {user}. Removing this user will also remove access '
                'to {node_path} unless another contributor re-authenticates.'
            ).format(
                category=node.project_or_component,
                user=removed.fullname,
                node_path=self.node_path
            )

    def after_remove_contributor(self, node, removed):
        """

        :param Node node:
        :param User removed:
        :return str: Alert message

        """
        if self.user_settings and self.user_settings.owner == removed:
            self.user_settings = None
            self.save()

            return (
                'Because the HDFS add-on for this project was authenticated '
                'by {user}, node path information has been deleted. You '
                'can re-enter this information on the <a href="{url}settings/">'
                'Settings</a> page.'.format(
                    user=removed.fullname,
                    url=node.url,
                )
            )

    def after_delete(self, node, user):
        self.deauthorize(Auth(user=user), log=True, save=True)
