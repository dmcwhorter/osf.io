import mock

from website.addons.hdfs.api import HdfsWrapper, HdfsObject


def create_mock_wrapper():
    mock_wrapper = mock.create_autospec(HdfsWrapper)
    mock_wrapper.get_wrapped_key.return_value = create_mock_object()
    return mock_wrapper


def create_mock_object():
    mock_key = mock.create_autospec(HdfsObject)
    mock_key.size = 1
    mock_key.hdfsKey = mock.MagicMock()
    mock_key.hdfsKey.get_contents_as_string.return_value = 'hi'
    return mock_key
