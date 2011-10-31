# A parser to read the todo.txt file
class TodotxtParser:

  todo_dir ="~/.todo/"
  todo_file ="$TODO_DIR/todo.txt"
  done_file ="$TODO_DIR/done.txt"
  report_file ="$TODO_DIR/report.txt"
  todo_actions_dir ="$TODO_DIR/actions"

  def __init__(self):
    pass
  
  def load(self):
    pass

  def getLocation(self,file):
    if file == 'todo':
      location = self.todo_file.replace('$TODO_DIR', self.todo_dir)
    elif file == 'todo_dir':
      location = self.todo_dir
    elif file == 'done':
      location = self.done_file.replace('$TODO_DIR', self.todo_dir)
    elif file == 'report':
      location = self.report_file.replace('$TODO_DIR', self.todo_dir)
    else:
      raise Exception("This is not a location")
    return location

  def getConfig(self,key):
    return getattr(self, key)
    
  def setConfig(self, data):
    for key, value in data.items():
      setattr(self, key, value)
