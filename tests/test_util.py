import os
import datetime
import uuid
import pytest
from unapi.util import generate_file_path
from dotenv import load_dotenv
from os import environ

load_dotenv()


@pytest.fixture
def local_storage_path():
    return environ["LOCAL_STORAGE_PATH"]


@pytest.fixture
def dt_str():
    return '2023-01-01_00-00-00'


@pytest.fixture
def uuid_str():
    return '00000000-0000-0000-0000-000000000000'


@pytest.fixture()
def mock_datetime(dt_str):
    class MockDateTime(datetime.datetime):
        @classmethod
        def utcnow(cls):
            return datetime.datetime.strptime(dt_str, '%Y-%m-%d_%H-%M-%S')

    return MockDateTime


class TestGenerateFilePath:
    #  Tests that a valid file path is generated
    def test_valid_file_path(self, dt_str, uuid_str, mocker, mock_datetime, local_storage_path):
        datetime.datetime.strptime(dt_str, '%Y-%m-%d_%H-%M-%S')
        mocker.patch('uuid.uuid4', return_value=uuid.UUID(uuid_str))
        mocker.patch('datetime.datetime', mock_datetime)
        file_name = 'test'
        file_extension = 'txt'
        full_file_name = file_name + '.' + file_extension
        file_path = generate_file_path(full_file_name, 'txt')
        assert file_path == fr'{local_storage_path}\{file_extension}\{dt_str}_{uuid_str}.{file_extension}'

    #  Tests that an empty file name raises an exception
    def test_empty_file_name(self):
        with pytest.raises(ValueError):
            generate_file_path('', 'txt')

    #  Tests that an invalid file type raises an exception
    def test_invalid_file_type(self):
        with pytest.raises(ValueError):
            generate_file_path('test.txt', '')

    #  Tests that a unique file name is generated
    def test_unique_file_name(self):
        file_name = 'test.txt'
        file_type = 'txt'
        file_path_1 = generate_file_path(file_name, file_type)
        file_path_2 = generate_file_path(file_name, file_type)
        assert os.path.basename(file_path_1) != os.path.basename(file_path_2)

    #  Tests that a valid file extension is generated
    def test_valid_file_extension(self):
        file_name = 'test.txt'
        file_type = 'txt'
        file_path = generate_file_path(file_name, file_type)
        assert os.path.splitext(file_path)[1] == f'.{file_type}'
