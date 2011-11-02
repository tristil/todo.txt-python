import os, re, sys

# A parser to read the todo.txt file
class TodotxtParser:

  todo_dir ="~/.todo"
  todo_file ="$TODO_DIR/todo.txt"
  done_file ="$TODO_DIR/done.txt"
  report_file ="$TODO_DIR/report.txt"
  todo_actions_dir ="$TODO_DIR/actions"

  def __init__(self):
    self.expandTodoDir()

  def load(self):
    self.data = {
        'todos' : {},
        'projects' : {},
        'contexts' : {},
        }

    todo_items = self.getRawTodos('todo')
    done_items = self.getRawTodos('done')

    id = 0
    for item_list in [todo_items, done_items]:
      for item in item_list:
        id += 1

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

  def writeData(self):
    todo_file = open(self.getLocation('todo'), 'w')
    done_file = open(self.getLocation('done'), 'w')
    
    for [index, todo] in self.data['todos'].items():
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
