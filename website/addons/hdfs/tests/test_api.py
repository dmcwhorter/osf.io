# -*- coding: utf-8 -*-
from nose.tools import *  # noqa
from tests.factories import ProjectFactory, UserFactory
from tests.base import OsfTestCase
from utils import create_mock_wrapper


# TODO: finish me
class TestHdfsApi(OsfTestCase):

    def setUp(self):

        super(TestHdfsApi, self).setUp()

        self.user = UserFactory()
        self.project = ProjectFactory(creator=self.user)
        self.project.add_addon('hdfs')
        self.project.creator.add_addon('hdfs')

        self.hdfs = create_mock_wrapper()

        self.node_settings = self.project.get_addon('hdfs')
        self.node_settings.user_settings = self.project.creator.get_addon('hdfs')
        self.node_settings.save()
