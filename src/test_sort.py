import unittest
from datetime import datetime
from os import path
from unittest.mock import patch, MagicMock

import sort


class TestPathStrMaker(unittest.TestCase):

    def test_maker_is_callable(self):
        fn = sort.get_path_str_maker('tester')
        self.assertTrue(callable(fn))

    @patch('sort._get_exif_datetime')
    def test_make_path_str(self, mock_get_exif_datetime):
        mock_get_exif_datetime.return_value = datetime(
            2020, 1, 1, 12, 54, 17)
        expected = path.join('tester', '2020', '01', '01_125417_test.jpg')
        make_path_str = sort.get_path_str_maker('tester')
        received = make_path_str('test.jpg')
        self.assertEqual(expected, received)

    @patch('sort._get_exif_datetime')
    def test_make_path_str_with_no_date(self, mock_get_exif_datetime):
        mock_get_exif_datetime.return_value = None
        expected = None
        make_path_str = sort.get_path_str_maker('tester')
        received = make_path_str('test.jpg')
        self.assertEqual(expected, received)


class TestPhotoMover(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_make_path_str = MagicMock()

    def test_maker_is_callable(self):
        fn = sort.get_photo_mover(self.mock_make_path_str)
        self.assertTrue(callable(fn))

    @patch('os.makedirs')
    @patch('os.rename')
    def test_make_path_str(self, mock_rename, mock_makedirs):
        self.mock_make_path_str.return_value = 'this/is/a/test/file.jpg'
        mv = sort.get_photo_mover(self.mock_make_path_str)
        mv('test.jpg')
        mock_makedirs.assert_called_with('this/is/a/test', exist_ok=True)
        mock_rename.assert_called_with('test.jpg', 'this/is/a/test/file.jpg')


class TestMoveAllPhotos(unittest.TestCase):
    @patch('os.walk')
    @patch('sort.get_photo_mover')
    def test_move_all_photos(self, mock_get_photo_mover, mock_walk):
        mock_move = MagicMock()
        mock_get_photo_mover.return_value = mock_move
        mock_walk.return_value = [
            ('/src', ('sub',), ('sub',)),
            ('/src/sub', (), ('photo1.jpg', 'photo2.jpg')),
        ]
        sort.sort_photos('src', mock_move)
        mock_move.assert_any_call('/src/sub/photo2.jpg')
        mock_move.assert_any_call('/src/sub/photo1.jpg')


class TestIsSubpath(unittest.TestCase):
    def test_is_sub_path(self):
        src = '/some/test/path'
        target = '/some/test/path/target'

        self.assertTrue(sort.is_sub_path(src, target))

    def test_is_not_sub_path(self):
        src = '/some/test/path/src'
        target = '/some/test/path/target'

        self.assertFalse(sort.is_sub_path(src, target))


if __name__ == '__main__':
    unittest.main()
