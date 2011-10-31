import unittest
import os, sys, shutil, re

sys.path.insert(0, os.path.abspath(os.path.abspath(__file__ )+ "/../../../"))

import todotxt

class TestTodotxtParser(unittest.TestCase):
  def setUp(self):
    self.maxDiff = None
    self.test_path = '/tmp/.todotest'
    self.parser = todotxt.TodotxtParser()
    os.mkdir(self.test_path)

    self.todo_file = open(self.test_path + '/todo.txt', 'w')
    self.done_file = open(self.test_path + '/done.txt', 'w')

  def tearDown(self):
    shutil.rmtree(self.test_path)

  def populate_file(self, file, text):
    file.write(text)
    file.close()

  def standard_setup(self):
    todo_text = """\
    Get things done @home
    Get some other things done @work
    Get yet other things done @work +bigproject\
    """

    done_text = "x 2011-10-30 Got things done @work +bigproject"
    self.populate_file(self.todo_file, todo_text)
    self.populate_file(self.done_file, done_text)
    
    self.parser.setConfig({
      'todo_dir' : self.test_path
      })

  def test_getRawData(self):
    self.standard_setup()

    data = self.parser.getRawData()
    expected_data = {
      'contexts' : {'home' : [1], 'work' : [2,3,4]},
      'projects' : {'default' : [1,2], 'bigproject' : [3,4]},
      'todos' :
      {
        1 : {'context' : 'home', 'project' : 'default', 'done' : False, 
          'item' : 'Get things done', 'completed': None},
        2 : {'context' : 'work', 'project' : 'default', 'done' : False,
          'item' : 'Get some other things done', 'completed': None},
        3 : {'context' : 'work', 'project' : 'bigproject', 'done' : False,
          'item' : 'Get yet other things done', 'completed': None},
        4 : {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'item' : 'Got things done', 'completed': '2011-10-30'},
      }
    }
    self.assertEqual(data, expected_data)

  def test_findUserDirectory(self):
    self.parser.setConfig({
      'todo_dir' : '~/.todo' 
      })
    self.assertTrue(
        re.match(r'\/home\/(.+?)\/.todo', self.parser.getLocation('todo_dir'))
        )

  def test_getRawTodos(self):
    self.populate_file(self.todo_file, "Get things done\n")
    self.populate_file(self.done_file, "Got things done\n")
    self.parser.setConfig({
      'todo_dir' : self.test_path
      })
    self.assertEqual(self.parser.getRawTodos(), ["Get things done"])
    self.assertEqual(self.parser.getRawTodos('done'), ["Got things done"])

  def test_getRawText(self):
    self.populate_file(self.todo_file, "Get things done\n")
    self.populate_file(self.done_file, "Got things done\n")

    self.parser.setConfig({
      'todo_dir' : self.test_path
      })
    self.assertEqual(self.parser.getRawText('todo'), "Get things done\n")
    self.assertEqual(self.parser.getRawText('done'), "Got things done\n")

  def test_setConfig(self):
    self.parser.setConfig({
      'todo_dir' : self.test_path,
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
    'todo_dir' : self.test_path,
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
