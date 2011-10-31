import unittest
import os, sys

sys.path.insert(0, os.path.abspath(__file__ + "/../../../") )

import todotxt

class TestTodotxtParser(unittest.TestCase):
  def setUp(self):
    self.parser = todotxt.TodotxtParser()

  def test_setConfig(self):
    self.parser.setConfig({
      'todo_dir' : '/tmp/.todotest',
      'report_file' : '/tmp/.todotest2/something.txt'
      })
    self.assertEqual(self.parser.getConfig('todo_dir'), '/tmp/.todotest')
    self.assertEqual(
        self.parser.getConfig('todo_file'), 
        '$TODO_DIR/todo.txt')
    self.assertEqual(
        self.parser.getConfig('report_file'), 
        '/tmp/.todotest2/something.txt')

  def test_getLocation(self):
    self.parser.setConfig({
    'todo_dir' : '/tmp/.todotest',
    })
    self.assertEqual(
      self.parser.getLocation('todo_dir'), 
      '/tmp/.todotest')
    self.assertEqual(
      self.parser.getLocation('todo'), 
      '/tmp/.todotest/todo.txt')
    self.assertEqual(
      self.parser.getLocation('report'), 
      '/tmp/.todotest/report.txt')
    self.assertEqual(
      self.parser.getLocation('done'), 
      '/tmp/.todotest/done.txt')

if __name__ == '__main__':
  unittest.main()
