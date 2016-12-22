# -*- coding: utf-8 -*-
from future.builtins import open as uopen
import os
import tempfile
import unittest
from unittest import TestCase

import six

from os3.fs.directory import Dir
from os3.fs.file import File
from os3.tests.base import MockTreeNode


class TestDirectory(MockTreeNode):

    def test_deep(self):
        self.assertEqual(set(Dir(self.directory).ls(depth=True).value('path')), self.deep_list_dir())

    def test_not_repeated(self):
        items = Dir(self.directory).ls(depth=True).value('path')
        self.assertEqual(len(items), len(set(items)))

    def test_max_deep(self):
        self.assertEqual(set(Dir(self.directory).ls(depth=0).value('path')), set(self.list_dir(full_path=True)))
        self.assertNotIn(os.path.join(self.directory, 'dir01/subdir01/subsubdir01'),
                         Dir(self.directory).ls(depth=1).value('path'))
        self.assertIn(os.path.join(self.directory, 'dir01/subdir01/subsubdir01'),
                      Dir(self.directory).ls(depth=2).value('path'))

    def test_filters_deep(self):
        # print(len([x for x in Dir(self.directory).ls(depth=True).filter(type='f')]))
        files = list(Dir(self.directory).ls(depth=True).filter(type='f').value('path'))
        six.assertCountEqual(self, files, set(files))
        self.assertEqual(len(files), (len(self.tree) + 1) * self.files_by_dir)

    def test_pre_filters_deep(self):
        from os3.fs.file import File
        files = list(Dir(self.directory).ls(type='f', depth=True))
        self.assertEqual(len(files), self.files_by_dir)
        for file in files:
            self.assertIsInstance(file, File)

    def test_print_format(self):
        self.assertIn(Dir(self.directory).name, Dir(self.directory).print_format())


class TestFile(TestCase):
    def setUp(self):
        self.filename = tempfile.NamedTemporaryFile().name

    def test_read(self):
        data = 'FOO' * 10
        with open(self.filename, 'w') as f:
            f.write(data)
        self.assertEqual(File(self.filename).read(), data)

    def test_repeat_read(self):
        data = 'SPAM' * 10
        with open(self.filename, 'w') as f:
            f.write(data)
        f = File(self.filename)
        self.assertEqual(f.read(), data)
        self.assertEqual(f.read(), data)

    def test_readlines(self):
        lines = list(map(str, range(10)))
        with open(self.filename, 'w') as f:
            f.write('\n'.join(lines))
        self.assertEqual(File(self.filename).readlines(breaklines=False), lines)
        with open(self.filename, 'wb') as f:
            f.write(b'\r\n'.join(map(lambda x: x.encode('utf-8'), lines)))
        self.assertEqual(File(self.filename).readlines(breaklines=False), lines)

    def test_readline(self):
        lines = list(map(str, range(10)))
        with open(self.filename, 'w') as f:
            f.write('\n'.join(lines))
        f = File(self.filename)
        read_lines = []
        while True:
            line = f.readline(breakline=False)
            if line is None:
                break
            read_lines.append(line)
        self.assertEqual(read_lines, lines)

    def test_read_n_data(self):
        data = u'ññññ'
        with uopen(self.filename, 'w') as f:
            f.write(data)
        self.assertEqual(File(self.filename).read(4), data)

    def test_read_n_bytes_data(self):
        data = u'ññññ'
        with uopen(self.filename, 'wb') as f:
            f.write(data.encode('utf-8'))
        self.assertEqual(File(self.filename).read(4, 'rb'), data.encode('utf-8')[:4])

    def tearDown(self):
        os.remove(self.filename)


class TestShorcuts(TestCase):
    def test_ls(self):
        from os3.sc import ls
        d1 = Dir('/foo').ls(depth=True)
        d2 = ls('/foo', depth=True)
        self.assertEqual(d1.path, d2.path)
        self.assertEqual(d1.depth, d2.depth)
        self.assertEqual(d1.__class__, d2.__class__)


if __name__ == '__main__':
    unittest.main()