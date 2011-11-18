import os, re, sys, string, time

# A parser to read the todo.txt file
class TodotxtParser:

  tracks_mapping = {
      'description' : 'item',
      'context' : 'context',
      'project' : 'project',
  }

  todo_dir ="~/.todo"
  todo_file ="$TODO_DIR/todo.txt"
  done_file ="$TODO_DIR/done.txt"
  report_file ="$TODO_DIR/report.txt"
  todo_actions_dir ="$TODO_DIR/actions"

  data = {}

  def __init__(self):
    self.expandTodoDir()

  def completeTodo(self, line_number):
    line = self.getLine(line_number)
    today = time.strftime('%Y-%m-%d') 
    line = '\nx ' + today + ' ' + line
    self.removeTodo(line_number)
    todo_file = open(self.getLocation('done'), 'a')
    todo_file.write(line)
    todo_file.close()

  def fetchRemoteData(self):
    self.remote_todos = self.remote_client.getTodos()

  def localTodoExists(self, tracks_id):
    todos = self.getTodos()
    for [index, todo] in todos.items():
      if todo['tracks_id'] == tracks_id:
        return True
    return False

  def importFromTracks(self, tracks_client):
    self.remote_client = tracks_client
    self.fetchRemoteData()
    count = 0
    for todo in self.remote_todos:
      if self.localTodoExists(todo['id']):
        continue

      new_todo = {}
      new_todo['tracks_id'] = todo['id']
      for [old_name, new_name] in self.tracks_mapping.items():
        count += 1
        if old_name in todo:
          new_todo[new_name] = todo[old_name]

      if todo['state'] == 'active':
        self.addTodo(new_todo)
      else:
        self.addTodo(new_todo, 'done')

  def getLine(self, line_number):
    todo_file = open(self.getLocation('todo'), 'r')
    lines = todo_file.readlines()
    todo_file.close()
    return lines[line_number - 1]

  def addTodo(self, data, todo_type = 'todo'):
    next_id = self.getNextId()
    if todo_type == 'todo':
      data['done'] = False
    elif todo_type == 'done':
      data['done'] = True
      data['completed'] = time.strftime('%Y-%m-%d') 
    self.data['todos'][next_id] = data
    self.data['ids'].append(next_id)

    if 'context' not in data:
      data['context'] = 'default'

    if 'tracks_id' not in data:
      data['tracks_id'] = None

    if data['context'] not in self.data['contexts']:
      self.addContext(data['context'])
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
    new_todo = '\n' + data['item']
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
    todo_text = string.join(lines, '\n')
    todo_file = open(self.getLocation('todo'), 'w')
    todo_file.write(todo_text)
    todo_file.close()

  def getTodos(self, todo_type = None):
    todos = self.data['todos'].items()
    todo_set = {}
    for [index, todo] in todos:
      if todo_type == None:
        todo_set[index] = todo
      elif todo['done'] == False and todo_type == 'todo':
        todo_set[index] = todo
      elif todo['done'] == True and todo_type == 'done':
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
        row = self.parseLine(item)
        self.data['todos'][id] = row

        if row['project'] not in self.data['projects']:
          self.data['projects'][row['project']] = [id]
        else:
          self.data['projects'][row['project']].append(id)

        if row['context'] not in self.data['contexts']:
          self.data['contexts'][row['context']] = [id]
        else:
          self.data['contexts'][row['context']].append(id)

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

    
    row = { 'item' : item,
            'done' : done,
            'context' : context,
            'project' : project,
            'completed' : completed,
            'tracks_id' : tracks_id
          }
    return row

  def makeLine(self,todo):
    line = ''
    if todo['done'] == True:
      line += 'x '
    if 'completed' in todo and todo['completed'] != None:
      line += todo['completed'] + ' '
    line += todo['item']
    if todo['context'] != 'default':
      line += ' @' + todo['context']
    if todo['project'] != 'default':
      line += ' +' + todo['project'] 

    if 'tracks_id' in todo and todo['tracks_id'] != None:
      line += ' tid:' + todo['tracks_id'] 

    return line

  def getTodoLines(self, type = 'todo'):
    lines = ""
    for [index, todo] in self.data['todos'].items():
      line = self.makeLine(todo)
      if todo['done'] == True and type =='done':
        lines += line + "\n"
      elif todo['done'] == False and type == 'todo':
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
      line = self.makeLine(todo)
      todo_file.write(line)
      if count != len(todos):
        todo_file.write('\n')
    todo_file.close()

  def setData(self, data):
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
