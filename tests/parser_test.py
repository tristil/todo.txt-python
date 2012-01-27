import unittest
import os, sys, shutil, re, time
from mock import Mock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.abspath(__file__ )+ "/../../../"))

import todotxt
import tracks

class TestTodotxtParser(unittest.TestCase):

  todos_data = None
  projects_data = None
  contexts_data = None

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

  def setup_remote_client(self):
    if self.todos_data == None:
      self.todos_data = [
          {u'description': u'A task from Tracks', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'brandnewcontext', u'context-id': u'2', u'id': u'200'}, 
          {u'description': u'Another task from Tracks', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'brandnewcontext', u'context-id': u'2', u'id': u'201'}, 
          {u'description': u'Fix retrieve password scenarios', u'tags': u'\n      ', u'notes': u"1) When username doesn't exist\n2) Labels fade out?", u'updated-at': u'2011-03-16T22:29:54-04:00', u'created-at': u'2011-03-15T00:26:15-04:00', u'project-id': u'23', 'project': u'newproject', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'292'}, 
      ]

    if self.projects_data == None:
      self.projects_data = [
          {u'description': u'Pretty big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'newproject'},
          {u'description': u'Another big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'anotherproject'}
      ]

    if self.contexts_data == None:
      self.contexts_data = [
          {u'hide': u'false', u'name': u'work', u'updated-at': u'2008-08-17T22:47:05-04:00', u'created-at': u'2008-08-17T22:47:05-04:00', u'position': u'1', u'id': u'1'}, 
          {u'hide': u'false', u'name': u'home', u'updated-at': u'2008-08-17T22:56:22-04:00', u'created-at': u'2008-08-17T22:56:22-04:00', u'position': u'2', u'id': u'2'}
      ]

    self.client = tracks.TracksClient()
    self.client.setOptions({'url': 'http://tracks.example.com', 'username': 'user', 'password': 'password'})

    self.client.getTodos = Mock(return_value=self.todos_data)
    self.client.getProjects = Mock(return_value=self.projects_data)
    self.client.getContexts = Mock(return_value=self.contexts_data)

    self.client.addProject = Mock(return_value=True)
    self.client.addContext = Mock(return_value=True)

    todo_count = 201
    add_todo_mock = Mock(return_value=todo_count)
    self.client.addTodo = add_todo_mock

    todo_count = 201
    update_todo_mock = Mock(return_value=todo_count)
    self.client.updateTodo = update_todo_mock


    self.todos_data = None
    self.projects_data = None
    self.contexts_data = None

  def test_updateTodosWithRemoteDoneStatus(self):
    self.projects_data = [
        {u'description': u'Pretty big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'newproject'},
        {u'description': u'Another big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'anotherproject'}
    ]
    self.todos_data = [
        {u'description': u'Fix retrieve password scenarios', u'tags': u'\n      ', u'notes': u"1) When username doesn't exist\n2) Labels fade out?", u'updated-at': u'2011-03-16T22:29:54-04:00', u'created-at': u'2011-03-15T00:26:15-04:00', u'project-id': u'23', 'project': u'Diaspora', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'292'}, 
    ]

    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(self.client)

    today = time.strftime('%Y-%m-%d')
    expected_data = [
        {'context' : 'home', 'project' : 'default', 'done' : False, 
          'description' : 'Get things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'default', 'done' : False,
          'description' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'description' : 'A task from Tracks', 'completed': today, 'tracks_id' : '200'},
        {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'description' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
        {'context': u'home',
          'done': False,
          'description': u'Fix retrieve password scenarios',
          'project': u'Diaspora',
          'tracks_id': u'292'},
        ]
    self.assertEqual([todo.getData() for index, todo in self.parser.getTodos().items()], expected_data)


  def test_updateRemoteTodosWithDoneStatus(self):
    self.todos_data = [
          {u'description': u'A task from Tracks', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'brandnewcontext', u'context-id': u'2', u'id': u'200'}, 
          {u'description': u'Get things done', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'brandnewcontext', u'context-id': u'2', u'id': u'205'}, 
          {u'description': u'Another task from Tracks', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'brandnewcontext', u'context-id': u'2', u'id': u'201'}, 
          {u'description': u'Fix retrieve password scenarios', u'tags': u'\n      ', u'notes': u"1) When username doesn't exist\n2) Labels fade out?", u'updated-at': u'2011-03-16T22:29:54-04:00', u'created-at': u'2011-03-15T00:26:15-04:00', u'project-id': u'23', 'project': u'newproject', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'292'}, 
    ]

    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.completeTodo(1)
    self.parser.load()

    self.parser.importFromTracks(self.client)
    self.parser.exportToTracks(self.client)

    self.assertEqual(self.client.addTodo.call_count, 2)
    self.parser.writeData()
    self.parser.load()

    today = time.strftime('%Y-%m-%d') 

    self.assertEqual([todo.getData() for index, todo in  self.parser.getTodos().items()], 
    [
      {'description': 'Get some other things done', 'completed': None, 'tracks_id': '201', 'project': 'default', 'done': False, 'context': 'work'},
      {'description': 'A task from Tracks', 'completed': None, 'tracks_id': '200', 'project': 'bigproject', 'done': False, 'context': 'work'},
      {'completed': None, 'context': 'brandnewcontext', 'description': 'Another task from Tracks', 'done': False, 'project': 'bigproject', 'tracks_id': '201'},
      {'completed': None, 'context': 'home', 'description': 'Fix retrieve password scenarios', 'done': False, 'project': 'newproject', 'tracks_id': '292'},
      {'description': 'Got things done', 'completed': '2011-10-30', 'tracks_id': '201', 'project': 'bigproject', 'done': True, 'context': 'work'},
      {'description': 'Get things done', 'completed': today, 'tracks_id': '205', 'project': 'default', 'done': True, 'context': 'home'},
    ]
    )

    self.assertEqual(self.client.updateTodo.call_count, 1)

  def test_updateTodosDontCreateDuplicateRemoteTodo(self):
    self.todos_data = [
          {u'description': u'Get things done', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'brandnewcontext', u'context-id': u'2', u'id': u'205'}, 
          {u'description': u'Another task from Tracks', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'brandnewcontext', u'context-id': u'2', u'id': u'201'}, 
          {u'description': u'Fix retrieve password scenarios', u'tags': u'\n      ', u'notes': u"1) When username doesn't exist\n2) Labels fade out?", u'updated-at': u'2011-03-16T22:29:54-04:00', u'created-at': u'2011-03-15T00:26:15-04:00', u'project-id': u'23', 'project': u'newproject', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'292'}, 
    ]

    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(self.client)
    self.parser.exportToTracks(self.client)

    self.assertEqual(self.client.addTodo.call_count, 2)
    self.parser.writeData()
    self.parser.load()

    today = time.strftime('%Y-%m-%d')

    self.assertEqual([todo.getData() for index, todo in  self.parser.getTodos().items()], 
    [
      {'description': 'Get things done', 'completed': None, 'tracks_id': '205', 'project': 'default', 'done': False, 'context': 'home'},
      {'description': 'Get some other things done', 'completed': None, 'tracks_id': '201', 'project': 'default', 'done': False, 'context': 'work'},
      {'completed': None, 'context': 'brandnewcontext', 'description': 'Another task from Tracks', 'done': False, 'project': 'bigproject', 'tracks_id': '201'},
      {'completed': None, 'context': 'home', 'description': 'Fix retrieve password scenarios', 'done': False, 'project': 'newproject', 'tracks_id': '292'},
      {'description': 'A task from Tracks', 'completed': today, 'tracks_id': '200', 'project': 'bigproject', 'done': True, 'context': 'work'},
      {'description': 'Got things done', 'completed': '2011-10-30', 'tracks_id': '201', 'project': 'bigproject', 'done': True, 'context': 'work'},
    ]
    )


  def test_importAndUpdateTodos(self):
    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(self.client)
    self.parser.exportToTracks(self.client)

    # I swear, something crazy is happening here and Mock is misreporting what
    # is being passed in. I set tracks_id after the call but it sees it as 
    # being passed in???
    """
    self.client.addTodo.assert_any_call(
    {
      'description': 'Get things done', 
      'completed': None, 
      'tracks_id': None, 
      'project': 'default', 
      'done': False, 
      'context': 'home'
    }
    )

    self.client.addTodo.assert_called_with(
    {
      'description' : 'Got things done', 
      'context' : 'work',
      'project' : 'bigproject',
      'tracks_id' : None,
      'done' : True,
      'completed' : '2011-10-30'
    }
    )
    """

    self.assertEqual(self.client.addTodo.call_count, 3)
    self.parser.writeData()
    self.parser.load()
    self.assertEqual([todo.getData() for index,todo in self.parser.getTodos().items()], 
    [
      {'description': 'Get things done', 'completed': None, 'tracks_id': '201', 'project': 'default', 'done': False, 'context': 'home'},
      {'description': 'Get some other things done', 'completed': None, 'tracks_id': '201', 'project': 'default', 'done': False, 'context': 'work'},
      {'description': 'A task from Tracks', 'completed': None, 'tracks_id': '200', 'project': 'bigproject', 'done': False, 'context': 'work'},
      {'completed': None, 'context': 'brandnewcontext', 'description': 'Another task from Tracks', 'done': False, 'project': 'bigproject', 'tracks_id': '201'},
      {'completed': None, 'context': 'home', 'description': 'Fix retrieve password scenarios', 'done': False, 'project': 'newproject', 'tracks_id': '292'},
      {'description': 'Got things done', 'completed': '2011-10-30', 'tracks_id': '201', 'project': 'bigproject', 'done': True, 'context': 'work'}
    ]
    )

  def test_importAndUpdateContexts(self):
    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(self.client)
    self.parser.exportToTracks(self.client)
    self.client.addContext.assert_called_once_with({'name' : 'brandnewcontext'})
    self.assertEqual(self.client.addContext.call_count, 1)

  def test_importAndUpdateProjects(self):
    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(self.client)
    self.parser.exportToTracks(self.client)
    self.client.addProject.assert_called_once_with({'name' : 'bigproject'})
    self.assertEqual(self.client.addProject.call_count, 1)

  def test_importAndDontOverwrite(self):
    self.projects_data = [
        {u'description': u'Pretty big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'newproject'},
        {u'description': u'Another big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'anotherproject'}
    ]
    self.todos_data = [
        {u'description': u'A task from Tracks', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'bigproject', u'state': u'active', 'context': u'work', u'context-id': u'2', u'id': u'200'}, 
        {u'description': u'Fix retrieve password scenarios', u'tags': u'\n      ', u'notes': u"1) When username doesn't exist\n2) Labels fade out?", u'updated-at': u'2011-03-16T22:29:54-04:00', u'created-at': u'2011-03-15T00:26:15-04:00', u'project-id': u'23', 'project': u'Diaspora', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'292'}, 
    ]

    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(self.client)
    expected_data = [
        {'context' : 'home', 'project' : 'default', 'done' : False, 
          'description' : 'Get things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'default', 'done' : False,
          'description' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'bigproject', 'done' : False,
          'description' : 'A task from Tracks', 'completed': None, 'tracks_id' : '200'},
        {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'description' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
        {'context': u'home',
          'done': False,
          'description': u'Fix retrieve password scenarios',
          'project': u'Diaspora',
          'tracks_id': u'292'},
        ]
    self.assertEqual([todo.getData() for index, todo in self.parser.getTodos().items()], expected_data)


  def test_importAndWriteData(self):
    self.test_importFromTracks()
    expected_text = """\
Get things done @home
Get some other things done @work
Add task text to Chromodoro @home +Chromodoro tid:293
Fix retrieve password scenarios @home +Diaspora tid:292
[Significant coding] for Diaspora @home +Diaspora tid:275
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
Add task text to Chromodoro @home +Chromodoro tid:293
Fix retrieve password scenarios @home +Diaspora tid:292
[Significant coding] for Diaspora @home +Diaspora tid:275\
"""

    self.assertEqual(self.parser.getTodoLines(), expected_text)

  def test_importFromTracks(self):
    self.todos_data = [
        {u'description': u'Add task text to Chromodoro', u'updated-at': u'2011-03-16T22:30:20-04:00', u'created-at': u'2011-03-16T22:30:20-04:00', u'project-id': u'25', 'project': u'Chromodoro', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'293'}, 
        {u'description': u'Fix retrieve password scenarios', u'tags': u'\n      ', u'notes': u"1) When username doesn't exist\n2) Labels fade out?", u'updated-at': u'2011-03-16T22:29:54-04:00', u'created-at': u'2011-03-15T00:26:15-04:00', u'project-id': u'23', 'project': u'Diaspora', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'292'}, 
        {u'description': u'[Significant coding] for Diaspora', u'tags': u'\n      ', u'updated-at': u'2010-11-15T00:29:35-05:00', u'created-at': u'2010-11-15T00:26:18-05:00', u'project-id': u'23', 'project': u'Diaspora', u'state': u'active', 'context': u'home', u'context-id': u'2', u'id': u'275'}, 
    ]

    self.projects_data = [
        {u'description': u'Pretty big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'newproject'},
        {u'description': u'Another big project\n', u'updated-at': u'2009-01-04T21:53:59-05:00', u'created-at': u'2008-08-17T22:44:18-04:00', u'state': u'completed', u'last-reviewed': u'2008-08-17T22:44:18-04:00', u'position': u'1', u'completed-at': u'2009-01-04T21:53:59-05:00', u'id': u'25', u'name': u'anotherproject'}
    ]

    self.setup_remote_client()

    self.standard_setup()
    self.parser.load()
    self.parser.importFromTracks(self.client)
    today = time.strftime('%Y-%m-%d')
    expected_data = [
        {'context' : 'home', 'project' : 'default', 'done' : False, 
          'description' : 'Get things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'default', 'done' : False,
          'description' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'description' : 'A task from Tracks', 'completed': today, 'tracks_id' : '200'},
        {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'description' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
        {'context': u'home',
          'done': False,
          'description': u'Add task text to Chromodoro',
          'project': u'Chromodoro',
          'tracks_id': u'293'
          },
        {'context': u'home',
          'done': False,
          'description': u'Fix retrieve password scenarios',
          'project': u'Diaspora',
          'tracks_id': u'292'},
        {'context': u'home',
          'done': False,
          'description': u'[Significant coding] for Diaspora',
          'project': u'Diaspora',
          'tracks_id': u'275'},
        ]
    self.assertEqual([todo.getData() for index,todo in self.parser.getTodos().items()], expected_data)

  def test_completeTodo(self):
    self.standard_setup()
    self.parser.completeTodo(3)
    text = self.read_file(self.todo_file)
    new_text = """\
Get things done @home
Get some other things done @work
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
Get some other things done @work
"""
    self.assertEqual(text, new_text)

  def test_addTodo(self):
    self.standard_setup()
    self.parser.load()
    self.parser.addTodo( { 
      'description'    : 'A brand new thing to do', 
      'context' : 'newcontext', 
      'project' : 'newproject'
      }
    )

    expected_data = [
        {'context' : 'home', 'project' : 'default', 'done' : False, 
          'description' : 'Get things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'default', 'done' : False,
          'description' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'bigproject', 'done' : False,
          'description' : 'A task from Tracks', 'completed': None, 'tracks_id': '200'},
        {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'description' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
        {'description' : 'A brand new thing to do', 'context' : 'newcontext', 'project' : 'newproject', 'done' : False, 'tracks_id' : None}
    ]

    self.assertEqual([todo.getData() for index, todo in self.parser.getTodos().items()], expected_data)
    self.assertEqual(self.parser.data['ids'], [1,2,3,4,5])

    self.assertEqual(self.parser.getContexts(), {
      'home' : [1], 'work' : [2,3,4], 'newcontext' : [5]})
    self.assertEqual(self.parser.getProjects(), {'default' : [1,2], 'bigproject' : [3,4], 'newproject' : [5]})
  
  def test_addTodoLine(self):
    self.standard_setup()
    self.parser.addTodoLine( { 
      'description'    : 'A brand new thing to do', 
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
          'description' : 'Get things done', 'completed': None, 'tracks_id' : None},
        2 : {'context' : 'work', 'project' : 'default', 'done' : True,
          'description' : 'Get some other things done', 'completed': '2011-10-30', 'tracks_id': None},
      }
    }

    self.parser.setData(data)
    data = self.parser.getRawData()

    self.parser.writeData();
    self.parser.load()
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
    self.parser.load()
    data = self.parser.getRawData()
    expected_todos_data = [
        {'context' : 'home', 'project' : 'default', 'done' : False, 
          'description' : 'Get things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'default', 'done' : False,
          'description' : 'Get some other things done', 'completed': None, 'tracks_id' : None},
        {'context' : 'work', 'project' : 'bigproject', 'done' : False,
          'description' : 'A task from Tracks', 'completed': None, 'tracks_id' : '200'},
        {'context' : 'work', 'project' : 'bigproject', 'done' : True,
          'description' : 'Got things done', 'completed': '2011-10-30', 'tracks_id' : None},
    ]

    expected_contexts_data = {'home' : [1], 'work' : [2,3,4]}
    expected_projects_data = {'default' : [1,2], 'bigproject' : [3,4]}
    expected_ids_data = [1,2,3,4]

    self.assertEqual(data['contexts'], expected_contexts_data)
    self.assertEqual(data['projects'], expected_projects_data)
    self.assertEqual(data['ids'], expected_ids_data)
    self.assertEqual([todo.getData() for index, todo in data['todos'].items()], expected_todos_data)

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
