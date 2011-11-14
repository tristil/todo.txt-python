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

  def importFromTracks(self, tracks_client):
    self.tracks_client = tracks_client
    todos = self.tracks_client.getTodos()
    for todo in todos:
      new_todo = {}
      new_todo['tracks_id'] = todo['id']
      for [old_name, new_name] in self.tracks_mapping.items():
        if old_name in todo:
          new_todo[new_name] = todo[old_name]
        self.addTodo(new_todo)

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

  def addTodoLine(self, data, todo_type = 'todo'):
    todo_file = open(self.getLocation(todo_type), 'a')
    new_todo = '\n' + data['item']
    if data['context'] != None:
      new_todo += " @" + data['context']
    if data['project'] != None:
      new_todo += " +" + data['project']
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

  def getTodos(self, todo_type = 'todo'):
    return self.data['todos']

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

        pattern = r'@(\w+?)( |$)'
        m = re.search(pattern, item)
        if m and m.group(1):
          context = m.group(1)
        else:
          context = 'default'
        item = re.sub(pattern, '', item)

        pattern = r'\+(\w+?)( |$)'
        m = re.search(pattern, item)
        if m and m.group(1):
          project = m.group(1)
        else:
          project = 'default'
        item = re.sub(pattern, '', item)

        pattern = r'^x '
        m = re.search(pattern, item, re.IGNORECASE)
        if m:
          done = True
        else:
          done = False
        item = re.sub(pattern, '', item)

        pattern = r'^(\d\d\d\d-\d\d-\d\d)'
        m = re.search(pattern, item)
        if m and m.group(1):
          completed = m.group(1)
        else:
          completed = None
        item = re.sub(pattern, '', item)

        item = item.strip()

        if project not in self.data['projects']:
          self.data['projects'][project] = [id]
        else:
          self.data['projects'][project].append(id)

        if context not in self.data['contexts']:
          self.data['contexts'][context] = [id]
        else:
          self.data['contexts'][context].append(id)

        row = { 'item' : item,
                'done' : done,
                'context' : context,
                'project' : project,
                'completed' : completed,
              }

        self.data['todos'][id] = row

  def makeLine(self,todo):
    line = ''
    if todo['done'] == True:
      line += 'x '
    if todo['completed'] != None:
      line += todo['completed'] + ' '
    line += todo['item']
    if todo['context'] != 'default':
      line += ' @' + todo['context']
    if todo['project'] != 'default':
      line += ' +' + todo['project'] 
    return line

  def printTodos(self, type = 'todo'):
    for [index, todo] in self.data['todos'].items():
      line = self.makeLine(todo)

      if todo['done'] == True and type =='done':
        print line
      elif todo['done'] == False and type == 'todo':
        print line

  def writeData(self):
    todo_file = open(self.getLocation('todo'), 'w')
    done_file = open(self.getLocation('done'), 'w')
    
    for [index, todo] in self.data['todos'].items():
      line = self.makeLine(todo)

      if todo['done'] == True:
        done_file.write(line + '\n')
      else:
        todo_file.write(line + '\n')
    todo_file.close()
    done_file.close()

  def setData(self, data):
    self.data = data

  def getRawData(self):
    self.load()
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

if __name__ == '__main__':
  todo_parser = TodotxtParser()
  print todo_parser.getRawData()
