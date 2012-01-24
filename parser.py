import os, re, sys, string, time
from todo import Todo

# A parser to read the todo.txt file
class TodotxtParser:

  tracks_mapping = {
      'description' : 'description',
      'context' : 'context',
      'project' : 'project',
  }

  todo_dir ="~/.todo"
  todo_file ="$TODO_DIR/todo.txt"
  done_file ="$TODO_DIR/done.txt"
  report_file ="$TODO_DIR/report.txt"
  todo_actions_dir ="$TODO_DIR/actions"

  verbose = False

  data = {}

  def __init__(self, **kargs):
    if 'verbose' in kargs and kargs['verbose'] == True:
      self.verbose = True

    self.expandTodoDir()

  def completeTodo(self, line_number):
    line = self.getLine(line_number)
    today = time.strftime('%Y-%m-%d') 
    line = '\nx ' + today + ' ' + line + '\n'
    self.removeTodo(line_number)
    todo_file = open(self.getLocation('done'), 'a')
    todo_file.write(line)
    todo_file.close()

  def fetchRemoteData(self):
    self.remote_todos = self.remote_client.getTodos()
    self.remote_projects = self.remote_client.getProjects()
    self.remote_contexts = self.remote_client.getContexts()

  def localTodoHasSameDescription(self,description):
    todos = self.getTodos()
    for [index, todo] in todos.items():
      if todo.getDescription() == description:
        return index 
    return False

  def getTodoByTracksId(self, tracks_id):
    todos = self.getTodos()
    for [index, todo] in todos.items():
      if todo.getTracksId() == tracks_id:
        return index
    return False

  def exportToTracks(self, tracks_client, refetch = False):
    if refetch:
      self.fetchRemoteData()

    added_projects = ['default']
    remote_projects = [remote_project['name'] for remote_project in self.remote_projects]

    new_projects = False

    for project in self.getProjects():
      if project not in remote_projects and project not in added_projects:
        if self.verbose: 
          print "Adding local project %s to remote Tracks instance" % project
        new_projects = True
        tracks_client.addProject({'name' : project})
        added_projects.append(project)
    if new_projects:
      self.remote_projects = self.remote_client.getProjects()

    added_contexts = ['default']
    remote_contexts = [remote_context['name'] for remote_context in self.remote_contexts]

    new_contexts = False

    for context in self.getContexts():
      if context not in remote_contexts and context not in added_contexts:
        if self.verbose: 
          print "Adding local context %s to remote Tracks instance" % context
        new_contexts = True
        tracks_client.addContext({'name' : context})
        added_contexts.append(context)

    if new_contexts:
      self.remote_contexts = self.remote_client.getContexts()

    remote_todos = [remote_todo['description'] for remote_todo in self.remote_todos]
    todos = self.getTodos().items()
    for [index, todo] in todos:
      tracks_id = None
      if todo.getDescription() not in remote_todos and todo.getTracksId() == None:
        if self.verbose: 
          print "Adding local todo %s to remote Tracks instance" % todo.getDescription()
        tracks_id = tracks_client.addTodo(todo)
        self.data['todos'][index].setTracksId(tracks_id)
      elif todo.getTracksId():
        for remote_todo in self.remote_todos:
          if remote_todo['id'] == todo.getTracksId():
            if todo.isDone() and remote_todo['state'] != 'completed':
              tracks_client.updateTodo(todo)
      
  def importFromTracks(self, tracks_client):
    if self.verbose: 
      print "Contacting remote Tracks instance"

    self.remote_client = tracks_client
    self.fetchRemoteData()
    count = 0
    for remote_todo in self.remote_todos:
      index_of_local_instance = self.getTodoByTracksId(remote_todo['id'])
      if index_of_local_instance:
        if remote_todo['state'] == 'completed':
          self.data['todos'][index_of_local_instance].setDone(True)
          self.data['todos'][index_of_local_instance].setCompletedDate(remote_todo['completed-at'][0:10])
        continue

      # Update the tid on the local todo instead of creating a new record remotely
      index_of_similar_todo = self.localTodoHasSameDescription(remote_todo['description'])
      if index_of_similar_todo != False:
        self.data['todos'][index_of_similar_todo].setTracksId(remote_todo['id'])
        continue

      new_todo = {}
      new_todo['tracks_id'] = remote_todo['id']
      for [old_name, new_name] in self.tracks_mapping.items():
        count += 1
        if old_name in remote_todo:
          new_todo[new_name] = remote_todo[old_name]

      if remote_todo['state'] == 'active':
        if self.verbose: 
          print "Adding active todo"

        self.addTodo(new_todo)
      else:
        if self.verbose: 
          print "Adding completed todo"
        self.addTodo(new_todo, 'done')

    # Doing this for now as a way to detect when a remote todo is set to 'done'
    # Not great, but /todos/done.xml takes too long to parse 
    # without some ability to limit results
    for index, local_todo in self.data['todos'].items():
      if local_todo.getTracksId() != None and not local_todo.isDone():
        remote_missing = True
        for remote_todo in self.remote_todos:
          if remote_todo['id'] == local_todo.getTracksId():
            remote_missing = False
            break
        if remote_missing:
          self.data['todos'][index].setDone(True)
          self.data['todos'][index].setCompletedDate(time.strftime('%Y-%m-%d'))

  def getLine(self, line_number):
    todo_file = open(self.getLocation('todo'), 'r')
    lines = todo_file.readlines()
    todo_file.close()
    return lines[line_number - 1]

  def addTodo(self, data, todo_type = 'todo'):
    todo = Todo(data)
    next_id = self.getNextId()
    if todo_type == 'todo':
      todo.setDone(False)
    elif todo_type == 'done':
      todo.setDone()
      todo.setCompletedDate(time.strftime('%Y-%m-%d'))
    self.data['todos'][next_id] = todo
    self.data['ids'].append(next_id)

    if 'context' not in data:
      todo.setContext('default')

    if 'tracks_id' not in data:
      todo.setTracksId(None)

    if todo.getContext() not in self.data['contexts']:
      self.addContext(todo.getContext())
    self.data['contexts'][data['context']].append(next_id)

    if 'project' not in data:
      data['project'] = 'default'

    if data['project'] not in self.data['projects']:
      self.addProject(data['project'])
    self.data['projects'][data['project']].append(next_id)

  def addContext(self, context):
    self.data['contexts'][context] = []

  def addProject(self, project):
    self.data['projects'][project] = []

  def makeTodoLine(self, data):
    new_todo = '\n' + data['description']
    if data['context'] != None:
      new_todo += " @" + data['context']
    if data['project'] != None:
      new_todo += " +" + data['project']
    if 'tracks_id' in data:
      new_todo += " tid:" + data['tracks_id']
    return new_todo

  def addTodoLine(self, data, todo_type = 'todo'):
    todo_file = open(self.getLocation(todo_type), 'a')
    new_todo = self.makeTodoLine(data)
    todo_file.write(new_todo)

  def removeTodo(self, line_number):
    todo_file = open(self.getLocation('todo'), 'r')
    lines = todo_file.readlines()
    lines = [line.strip() for line in lines]
    todo_file.close()
    lines.pop(line_number - 1)
    todo_text = string.join(lines, '\n') + '\n'
    todo_file = open(self.getLocation('todo'), 'w')
    todo_file.write(todo_text)
    todo_file.close()

  def getTodos(self, todo_type = None):
    todos = self.data['todos'].items()
    todo_set = {}
    for [index, todo] in todos:
      if todo_type == None:
        todo_set[index] = todo
      elif todo.isDone() == False and todo_type == 'todo':
        todo_set[index] = todo
      elif todo.isDone() == True and todo_type == 'done':
        todo_set[index] = todo
    return todo_set

  def getData(self):
    return self.data

  def getContexts(self):
    return self.data['contexts']

  def getProjects(self):
    return self.data['projects']

  def getNextId(self):
    return max(self.data['ids']) + 1

  def load(self):
    self.data = {
        'todos' : {},
        'projects' : {},
        'contexts' : {},
        'ids' : [],
        }

    todo_items = self.getRawTodos('todo')
    done_items = self.getRawTodos('done')

    id = 0
    for item_list in [todo_items, done_items]:
      for item in item_list:
        id += 1
        self.data['ids'].append(id)
        todo = self.parseLine(item)
        self.data['todos'][id] = todo

        if todo.getProject() not in self.data['projects']:
          self.data['projects'][todo.getProject()] = [id]
        else:
          self.data['projects'][todo.getProject()].append(id)

        if todo.getContext() not in self.data['contexts']:
          self.data['contexts'][todo.getContext()] = [id]
        else:
          self.data['contexts'][todo.getContext()].append(id)

  def parseLine(self, item):
    pattern = r'@(\w+?)( |$)'
    m = re.search(pattern, item)
    if m and m.group(1):
      context = m.group(1)
    else:
      context = 'default'
    item = re.sub(pattern, '', item).strip()

    pattern = r'\+(\w+?)( |$)'
    m = re.search(pattern, item)
    if m and m.group(1):
      project = m.group(1)
    else:
      project = 'default'
    item = re.sub(pattern, '', item).strip()

    pattern = r'^x '
    m = re.search(pattern, item, re.IGNORECASE)
    if m:
      done = True
    else:
      done = False
    item = re.sub(pattern, '', item).strip()

    pattern = r'^(\d\d\d\d-\d\d-\d\d)'
    m = re.search(pattern, item)
    if m and m.group(1):
      completed = m.group(1)
    else:
      completed = None
    item = re.sub(pattern, '', item).strip()

    pattern = r'tid\:(\w+)( |$)'
    m = re.search(pattern, item)
    if m and m.group(1):
      tracks_id = m.group(1)
    else:
      tracks_id = None
    item = re.sub(pattern, '', item).strip()

    row = { 'description' : item,
            'done' : done,
            'context' : context,
            'project' : project,
            'completed' : completed,
            'tracks_id' : tracks_id
          }

    todo = Todo(row)
    return todo

  def getTodoLines(self, type = 'todo'):
    lines = ""
    for [index, todo] in self.data['todos'].items():
      line = todo.getTextLine()
      if todo.isDone() == True and type =='done':
        lines += line + "\n"
      elif todo.isDone() == False and type == 'todo':
        lines += line + "\n"
    return lines.strip()

  def writeData(self):
    todo_todos = self.getTodos('todo')
    self.writeTodosToFile(todo_todos)
    done_todos = self.getTodos('done')
    self.writeTodosToFile(done_todos, 'done')

  def writeTodosToFile(self, todos, todo_type = 'todo'):
    todo_file = open(self.getLocation(todo_type), 'w')
    count = 0
    for [index, todo] in todos.items():
      count += 1
      line = todo.getTextLine()
      todo_file.write(line)
      if count != len(todos):
        todo_file.write('\n')
    todo_file.close()

  def setData(self, data):
    if 'todos' in data:
      for index, todo in data['todos'].items():
        data['todos'][index] = Todo(todo)
        
    self.data = data

  def getRawData(self):
    return self.data

  def getRawTodos(self, type = 'todo'):
    text = self.getRawText(type)
    return text.strip().split("\n")

  def getRawText(self, file):
    f = open(self.getLocation(file), 'r')
    text = f.read()
    f.close()
    return text

  def getLocation(self, file):
    if file == 'todo':
      location = self.todo_file.replace('$TODO_DIR', self.todo_dir)
    elif file == 'todo_dir':
      location = self.todo_dir
    elif file == 'done':
      location = self.done_file.replace('$TODO_DIR', self.todo_dir)
    elif file == 'report':
      location = self.report_file.replace('$TODO_DIR', self.todo_dir)
    else:
      raise Exception("This is not a location type: " + file)
    return location

  def getConfig(self,key):
    return getattr(self, key)

  def expandTodoDir(self):
    if '~' in self.todo_dir:
      self.todo_dir = self.todo_dir.replace('~', '/home/' + os.getlogin())
    
  def setConfig(self, data):
    for key, value in data.items():
      setattr(self, key, value)
    self.expandTodoDir()
