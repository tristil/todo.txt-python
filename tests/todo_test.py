import unittest, os, sys

sys.path.insert(0, os.path.abspath(os.path.abspath(__file__ )+ "/../../../"))

import todotxt

class TestTodo(unittest.TestCase):

  todo_data = {
      'description' : 'Got things done', 
      'context' : 'work',
      'project' : 'bigproject',
      'tracks_id' : None,
      'done' : True,
      'completed' : '2011-10-30'
  }

  def test_createTodo(self):
    todo = todotxt.Todo()
    todo = todotxt.Todo(self.todo_data)

  def test_setData(self):
    todo = todotxt.Todo()
    todo.setData(self.todo_data)

  def test_getData(self):
    todo = todotxt.Todo()
    todo.setData(self.todo_data)
    self.assertEqual(todo.getData(), self.todo_data)
    self.assertEqual(todo.getDescription(), 'Got things done')
    self.assertEqual(todo.getProject(), 'bigproject')
    self.assertEqual(todo.getContext(), 'work')
    self.assertEqual(todo.getTracksId(), None)
    self.assertEqual(todo.isDone(), True)
    self.assertEqual(todo.getCompletedDate(), '2011-10-30')

  def test_getTextLine(self):
    todo = todotxt.Todo()
    todo.setData(self.todo_data)
    self.assertEqual(todo.getTextLine(), 'x 2011-10-30 Got things done @work +bigproject')


    
