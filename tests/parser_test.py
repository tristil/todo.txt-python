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

    self.todo_file = self.test_path + '/todo.txt'
    self.done_file = self.test_path + '/done.txt'

  def tearDown(self):
    shutil.rmtree(self.test_path)

  def populate_file(self, file, text):
    todo_file = open(file, 'w')
    todo_file.write(text)
    todo_file.close()

  def read_file(self, file):
    todo_file = open(file, 'r')
    text = todo_file.read()
    todo_file.close()
    return text

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

  def test_completeTodo(self):
    self.standard_setup()
    self.parser.completeTodo(3)
    text = self.read_file(self.todo_file)
    new_text = """\
Get things done @home
Get some other things done @work\
"""
    self.assertEqual(text, new_text)
    text = self.read_file(self.done_file)
    pattern = r'\nx \d\d\d\d-\d\d-\d\d Get yet other things done @work \+bigproject'
    self.assertTrue(re.search(pattern, text))

  def test_removeTodo(self):
    self.standard_setup()
    self.parser.removeTodo(3)
    text = self.read_file(self.todo_file)
    new_text = """\
Get things done @home
Get some other things done @work\
"""
    self.assertEqual(text, new_text)
  
  def test_addTodo(self):
    self.standard_setup()
    self.parser.addTodo( { 
      'item'    : 'A brand new thing to do', 
      'context' : 'newcontext', 
      'project' : 'newproject'
      }
    )
    text = self.read_file(self.todo_file)
    new_text = """\
Get things done @home
Get some other things done @work
Get yet other things done @work +bigproject
A brand new thing to do @newcontext +newproject\
"""
    self.assertEqual(text, new_text)

  def test_writeData(self):
    self.standard_setup()

    data = {
      'contexts' : {'home' : [1], 'work' : [2]},
      'projects' : {'default' : [1], 'bigproject' : [2]},
      'todos' :
      {
        1 : {'context' : 'home', 'project' : 'default', 'done' : False, 
          'item' : 'Get things done', 'completed': None},
        2 : {'context' : 'work', 'project' : 'default', 'done' : True,
          'item' : 'Get some other things done', 'completed': '2011-10-30'},
      }
    }

    self.parser.setData(data)
    self.parser.writeData();

    data = self.parser.getRawData()

    f = open(self.parser.getLocation('todo'), 'r')
    todo_text = f.read()
    f.close()

    self.assertEqual(todo_text, 'Get things done @home\n')

    f = open(self.parser.getLocation('done'), 'r')
    done_text = f.read()
    f.close()

    self.assertEqual(done_text, 'x 2011-10-30 Get some other things done @work\n')

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