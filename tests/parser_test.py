import unittest
import os, sys, shutil, re
from mock import Mock

sys.path.insert(0, os.path.abspath(os.path.abspath(__file__ )+ "/../../../"))

import todotxt
import tracks

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
A task from Tracks @work +bigproject tid:200\
"""

    done_text = "x 2011-10-30 Got things done @work +bigproject"
    self.populate_file(self.todo_file, todo_text)
    self.populate_file(self.done_file, done_text)
    
    self.parser.setConfig({
      'todo_dir' : self.test_path
      })

  def test_importAndWriteData(self):
    self.test_importFromTracks()
    expected_text = """\
Get things done @home
Get some other things done @work
A task from Tracks @work +bigproject tid:200
Add task text to Chromodoro @home +Chromodoro tid:293
Fix retrieve password scenarios @home +Diaspora tid:292
[Significant coding] for Diaspora @home +Diaspora tid:275\
"""
    self.parser.writeData()

    f = open(self.parser.getLocation('todo'), 'r')
    todo_text = f.read()
    f.close()

    self.assertEqual(todo_text, expected_text)


  def test_getTodoLines(self):
    self.test_importFromTracks()
    expected_text = """\
Get things done @home
Get some other things done @work
A task from Tracks @work +bigproject tid:200
Add task text to Chromodoro @home +Chromodoro tid:293
Fix retrieve password scenarios @home +Diaspora tid:292
[Significant coding] for Diaspora @home +Diaspora tid:275\
"""

    self.assertEqual(self.parser.getTodoLines(), expected_text)

  def test_importFromTracks(self):
    client = tracks.TracksClient()

    import_data = [
        {u'description': u'Add task text to Chromodoro', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'Chromodoro', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'293'}, 
        {u'description': u'Fix retrieve password scenarios', u'tags': u'\n      ', u'notes': u"1) When username doesn't exist\n2) Labels fade out?", u'updated-at': u'2011-03-16T22:29:54-04:00', u'created-at': u'2011-03-15T00:26:15-04:00', u'project-id': u'23', 'project': u'Diaspora', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'292'}, 
        {u'description': u'[Significant coding] for Diaspora', u'tags': u'\n      ', u'updated-at': u'2010-11-15T00:29:35-05:00', u'created-at': u'2010-11-15T00:26:18-05:00', u'project-id': u'23', 'project': u'Diaspora', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'275'}, 
    ]

    client.getTodos = Mock(return_value=import_data)
    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(client)
    expected_data = {
        1 : {'context' : 'home', 'project' : 'default', 'done' : False, 
          'item' : 'Get things done', 'completed': None, 'tracks_id' : None},
        2 : {'context' : 'work', 'project' : 'default', 'done' : False,
          'item' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        3 : {'context' : 'work', 'project' : 'bigproject', 'done' : False,
          'item' : 'A task from Tracks', 'completed': None, 'tracks_id' : '200'},
        4 : {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'item' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
        5: {'context': u'home',
          'done': False,
          'item': u'Add task text to Chromodoro',
          'project': u'Chromodoro',
          'tracks_id': u'293'
          },
        6: {'context': u'home',
          'done': False,
          'item': u'Fix retrieve password scenarios',
          'project': u'Diaspora',
          'tracks_id': u'292'},
        7: {'context': u'home',
          'done': False,
          'item': u'[Significant coding] for Diaspora',
          'project': u'Diaspora',
          'tracks_id': u'275'},
        }
    self.assertEqual(self.parser.getTodos(), expected_data)

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
    pattern = r'\nx \d\d\d\d-\d\d-\d\d A task from Tracks @work \+bigproject'
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
    self.parser.load()
    self.parser.addTodo( { 
      'item'    : 'A brand new thing to do', 
      'context' : 'newcontext', 
      'project' : 'newproject'
      }
    )

    expected_data = {
        1 : {'context' : 'home', 'project' : 'default', 'done' : False, 
          'item' : 'Get things done', 'completed': None, 'tracks_id' : None},
        2 : {'context' : 'work', 'project' : 'default', 'done' : False,
          'item' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        3 : {'context' : 'work', 'project' : 'bigproject', 'done' : False,
          'item' : 'A task from Tracks', 'completed': None, 'tracks_id': '200'},
        4 : {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'item' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
        5 : {'item' : 'A brand new thing to do', 'context' : 'newcontext', 'project' : 'newproject', 'done' : False, 'tracks_id' : None}
    }

    self.assertEqual(self.parser.getTodos(), expected_data)
    self.assertEqual(self.parser.data['ids'], [1,2,3,4,5])

    self.assertEqual(self.parser.getContexts(), {
      'home' : [1], 'work' : [2,3,4], 'newcontext' : [5]})
    self.assertEqual(self.parser.getProjects(), {'default' : [1,2], 'bigproject' : [3,4], 'newproject' : [5]})
  
  def test_addTodoLine(self):
    self.standard_setup()
    self.parser.addTodoLine( { 
      'item'    : 'A brand new thing to do', 
      'context' : 'newcontext', 
      'project' : 'newproject'
      }
    )
    text = self.read_file(self.todo_file)
    new_text = """\
Get things done @home
Get some other things done @work
A task from Tracks @work +bigproject tid:200
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
          'item' : 'Get things done', 'completed': None, 'tracks_id' : None},
        2 : {'context' : 'work', 'project' : 'default', 'done' : True,
          'item' : 'Get some other things done', 'completed': '2011-10-30', 'tracks_id': None},
      }
    }

    self.parser.setData(data)
    self.parser.writeData();
    self.parser.load()
    data = self.parser.getRawData()

    f = open(self.parser.getLocation('todo'), 'r')
    todo_text = f.read()
    f.close()

    self.assertEqual(todo_text, 'Get things done @home')

    f = open(self.parser.getLocation('done'), 'r')
    done_text = f.read()
    f.close()

    self.assertEqual(done_text, 'x 2011-10-30 Get some other things done @work')

  def test_getRawData(self):
    self.standard_setup()
    self.parser.load()
    data = self.parser.getRawData()
    expected_data = {
      'contexts' : {'home' : [1], 'work' : [2,3,4]},
      'projects' : {'default' : [1,2], 'bigproject' : [3,4]},
      'todos' :
      {
        1 : {'context' : 'home', 'project' : 'default', 'done' : False, 
          'item' : 'Get things done', 'completed': None, 'tracks_id' : None},
        2 : {'context' : 'work', 'project' : 'default', 'done' : False,
          'item' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        3 : {'context' : 'work', 'project' : 'bigproject', 'done' : False,
          'item' : 'A task from Tracks', 'completed': None, 'tracks_id' : '200'},
        4 : {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'item' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
      },
      'ids' : [1,2,3,4]
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
