What is it?
-----------
This is a simple Python library for reading and writing todo.txt files (i.e.,
the dirt-simple text format used by the `todo.txt bash script <http://todotxt.com>`_ by
Gina Trapani. Mostly it is an excuse for me to brush up on TDD in Python. 

This library was developed in conjunction with the `tracks-python library <https://github.com/tristil/tracks-python>`_,
for interfacing with Tracks instances (`Tracks <https://github.com/TracksApp/tracks>`_ 
is a GTD todo list web application), and is included as a sub-project in the 
`Tracks-Sync extension <https://github.com/tristil/Todo.txt-Tracks-Sync>`_ for todo.txt. The reason
for using Python for this integration was to have a todo.txt parsing library
that wasn't written in Bash but which would run on most Linux servers.

Major caveats for using this library are:

* It may not see much more active development.
* I didn't implement anything with regard to Priority.
* I don't understand relative module inclusion in Python very well. There's a
  lot of appending the path of the parent directory to the paths list.
* There might be a hard dependency on the Tracks module.
* If you run this on your beloved todo.txt files, be sure to MAKE A BACKUP
  first. It could very well erase or jumble your data.

Usage
-----
::  

  # instantiate the parser
  parser = TodotxtParser(verbose = True)

  # read the todo.txt files from the usual place (~/.todo)
  parser.load()

  # else change the default path
  parser.setConfig({'todo_dir' : '/tmp/.todo'})
  parser.load()

  # get the todos
  todos = parser.getTodos()

  # add a todo
  parser.addTodo( { 
      'description'    : 'A brand new thing to do', 
      'context' : 'newcontext', 
      'project' : 'newproject'
      }
  )

  # write the new data back to file
  parser.writeData()

  # remove a todo from the file
  parser.removeTodo(2)

  # Complete a todo 
  parser.completeTodo(1)

Feedback
--------
If somebody actually has a use for this library and has additional
requirements/ bugs / patches, go ahead and submit them as Github issues and I
will respond to them as quickly as possible.
