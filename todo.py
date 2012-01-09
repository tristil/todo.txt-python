# Object representing a todo 
class Todo:
  data = {}

  def __init__(self, data = None):
    if data:
      self.setData(data)

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

  def setTracksId(self, tracks_id):
    if tracks_id == None:
      self.data['tracks_id'] = None
    else:
      self.data['tracks_id'] = str(tracks_id)

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
    if self.isDone() == True:
      line += 'x '
    if self.getCompletedDate() != None:
      line += self.getCompletedDate() + ' '
    line += self.getDescription()
    if self.getContext() != 'default':
      line += ' @' + self.getContext()
    if self.getProject() != 'default':
      line += ' +' + self.getProject() 

    if self.getTracksId() != None:
      line += ' tid:' + self.getTracksId()

    return line

