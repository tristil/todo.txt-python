# Object representing a todo 
class Todo:
  data = {}

  def __init__(self, data = None):
    if data:
      self.setData(data)

  def setAttribute(self, key, value):
    self.data[key] = value

  def setData(self, data):
    self.data = data

  def getData(self):
    return self.data

  def getDescription(self):
    return self.data['description']

  def getProject(self):
    return self.data['project']

  def getContext(self):
    return self.data['context']

  def getTracksId(self):
    return self.data['tracks_id']

  def isDone(self):
    return self.data['done']

  def setDone(self, done = True):
    self.data['done'] = done

  def getCompletedDate(self):
    if 'completed' in self.data:
      return self.data['completed']
    else:
      return None

  def setCompletedDate(self, date):
    self.data['completed'] = date

  def getTextLine(self):
    line = ''
    if self.data['done'] == True:
      line += 'x '
    if 'completed' in self.data and self.data['completed'] != None:
      line += self.data['completed'] + ' '
    line += self.data['description']
    if self.data['context'] != 'default':
      line += ' @' + self.data['context']
    if self.data['project'] != 'default':
      line += ' +' + self.data['project'] 

    if 'tracks_id' in self.data and self.data['tracks_id'] != None:
      line += ' tid:' + self.data['tracks_id'] 

    return line
