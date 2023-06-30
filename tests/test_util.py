import os
import datetime
import uuid
from pathlib import Path
import pytest
from unapi.util import generate_file_path, save_file
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


class TestSaveFile:
    #  Tests that the function saves a file successfully when given a valid file path and content.
    def test_save_file_success(self, tmp_path):
        file_path = Path(tmp_path) / "test.txt"
        file_content = b"test content"
        assert save_file(file_path, file_content) == file_path
        assert file_path.read_bytes() == file_content

    #  Tests that the function creates the necessary directories when make_dirs is True.
    def test_save_file_create_dirs(self, tmp_path):
        file_path = Path(tmp_path) / "dir1/dir2/test.txt"
        file_content = b"test content"
        assert save_file(file_path, file_content) == file_path
        assert file_path.read_bytes() == file_content

    #  Tests that the function returns None when the file path is None.
    def test_save_file_file_path_none(self, tmp_path):
        file_content = b"test content"
        assert save_file(None, file_content) is None

    #  Tests that the function returns None when the file path is an empty string.
    def test_save_file_file_path_empty_string(self, tmp_path):
        file_content = b"test content"
        assert save_file("", file_content) is None

    #  Tests that the function returns None when an unexpected error occurs.
    def test_save_file_unexpected_error(self, tmp_path, mocker):
        file_path = tmp_path / "test.txt"
        file_content = b"test content"
        mocker.patch("builtins.open", side_effect=Exception("Unexpected error"))
        assert save_file(file_path, file_content) is None
