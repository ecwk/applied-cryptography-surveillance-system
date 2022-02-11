import re
import os
from msvcrt import getch
from copy import deepcopy

from util.tools import clearConsole

from pprint import pprint

menuParts = {
  'top': '═',
  'bottom': '─',
  'left': '│',
  'right': '║',
  'tl': '╒',
  'tr': '╗',
  'bl': '└',
  'br': '╜'
}

def view(
  title = [],
  bodyHeader = [], body = [],
  itemsHeader = [], items = [],
  exitStr = None, activeState = 1,
  ):
  
  if not exitStr: # Python's function default won't work for this as the variable does not reset whenever the function is re run within a while loop, causing unwanted behaviour
    exitStr = { 'text': 'Back' }

  ## PRINTING MENU ##
  width = 50
  m = menuParts
  top = f'{ m["tl"] }{ m["top"] * (width - 2) }{ m["tr"] }'
  bottom = f'{ m["bl"] }{ m["bottom"] * (width - 2) }{ m["br"] }'
  hr = m['left'] + (m['bottom'] * (width-10)).center(width-2) + m['right']
  indentation = ' ' * 4

  # Title
  titleStr = ''
  if title:
    for i, line in enumerate(title):
      styledLine = ''
      for n, phrase in enumerate(line['text']):
        phraseColor = None
        if line.get('color'):
          phraseColor = line['color'][n]
        phraseTypes = None
        if line.get('types'):
          phraseTypes = line['types'][n]
        phrase = StyledStr(phrase, {
          'color': phraseColor,
          'types': phraseTypes
        }).str

        styledLine += phrase

      styledLine = m['left'] + alignCenter(styledLine, width - 2) + m['right']
      title[i] = styledLine

    titleStr += top + '\n'
    for e in title:
      titleStr += e + '\n'
    titleStr += bottom + '\n'

  # Body
  bodyStr = ''
  if body:
    for i, line in enumerate(bodyHeader):
      styledLine = ''
      for n, phrase in enumerate(line['text']):
        phraseColor = None
        if line.get('color'):
          phraseColor = line['color'][n]
        phraseTypes = None
        if line.get('types'):
          phraseTypes = line['types'][n]
        phrase = StyledStr(phrase, {
          'color': phraseColor,
          'types': phraseTypes
        }).str

        styledLine += phrase
      styledLine = m['left'] + alignCenter(styledLine, width - 2) + m['right']
      bodyHeader[i] = styledLine

    for i, line in enumerate(body):
      styledLine = ''
      for n, phrase in enumerate(line['text']):
        phraseColor = None
        if line.get('color'):
          phraseColor = line['color'][n]
        phraseTypes = None
        if line.get('types'):
          phraseTypes = line['types'][n]
        phrase = StyledStr(phrase, {
          'color': phraseColor,
          'types': phraseTypes
        }).str

        styledLine += phrase
      styledLine = m['left'] + alignLeft(indentation + styledLine, width - 2 - len(indentation)) + m['right']
      body[i] = styledLine

    bodyStr += top + '\n'
    for e in bodyHeader:
      bodyStr += e + '\n'
    bodyStr += hr + '\n'
    for e in body:
      bodyStr += e + '\n'
    bodyStr += hr + '\n'
    bodyStr += bottom + '\n'

  # Items Header

  itemsHeaderStr = ''
  if items:
    if not itemsHeader:
      itemsHeader = [{ 'text': ['Select'], 'types': [['bold']] }]
    for i, line in enumerate(itemsHeader):
      styledLine = ''
      for n, phrase in enumerate(line['text']):
        phraseColor = None
        if line.get('color'):
          phraseColor = line['color'][n]
        phraseTypes = None
        if line.get('types'):
          phraseTypes = line['types'][n]
        phrase = StyledStr(phrase, {
          'color': phraseColor,
          'types': phraseTypes
        }).str

        styledLine += phrase
      styledLine = m['left'] + alignCenter(styledLine, width - 2) + m['right']
      itemsHeader[i] = styledLine

    itemsHeaderStr += top + '\n'
    for e in itemsHeader:
      itemsHeaderStr += e + '\n'
    itemsHeaderStr += hr + '\n'

    # Items
    items.append(exitStr)
    for i, item in enumerate(items):
      if i == len(items) - 1:
        items[-1]['text'] = '0. ' + items[-1]['text']
      else:
        items[i]['text'] = f'{i+1}. {item["text"]}'
  cloneItems = deepcopy(items)

  # hideHelp = False
  activeIndex = activeState - 1
  while True:
    clearConsole()
    menuScreen = ''
    menuScreen += titleStr
    menuScreen += bodyStr
    menuScreen += itemsHeaderStr

    itemsStr = ''
    for i, item in enumerate(cloneItems):
      if i == activeIndex:
        cloneItems[i]['text'] = StyledStr(items[i]['text'], {
          'color': [(0 ,0, 0), (0, 220, 164)], 
          'types': ['bold']
        }).str
      else:
        cloneItems[i]['text'] = StyledStr(items[i]['text']).str
      itemsStr += f'{m["left"]}{alignLeft(indentation + item["text"], width-2-len(indentation))}{m["right"]}' + '\n'
    itemsStr += hr + '\n'
    menuScreen += itemsStr
    menuScreen += bottom
    print(menuScreen)

    key = getch()
    #  ctrl + h
    if key == b'\x08':
      hideHelp = False if hideHelp else True
    # up
    elif key.lower() == b'w': 
      if not activeIndex == 0:
        activeIndex -= 1
      else:
        activeIndex = len(cloneItems) - 1
    # down
    elif key.lower() == b's':
      if not activeIndex == len(cloneItems) - 1:
        activeIndex += 1
      else:
        activeIndex = 0
    # enter
    elif key == b'\r':
      if activeIndex == len(cloneItems)-1:
        return 0
      return activeIndex + 1
    # esc
    elif key == b'\x1b':
      if exitStr == 'Exit':
        return 0
      return 0
    elif key.decode().isnumeric():
      if int(key) <= len(items) - 1:
        return int(key)


class StyledStr():
  def __init__(self,
    str,
    style={
      'color': None, # [(255,0,0), (0,0,255)], left targets foreground, right targets background
      'types': None, #['bold', 'italic', 'underline']
    },
    ):
    self.str = str
    self.style = style
    self.enableWindowsSupport()
    
    if self.style.get('color'):
      self.str = addColor(self.str, self.style['color'])
    if self.style.get('types'):
      self.str = addType(self.str, self.style['types'])
    if not (self.style.get('color') and self.style.get('types')):
      self.str = '\033[0m' + self.str
    self.str = self.str + '\033[0m'

  def enableWindowsSupport(self):
    if os.name == 'nt':
      os.system('')

  def __str__(self):
    return self.str


def addColor(string, color): # color e.g. [(255,0,0), (0,0,255)]
  coloredStr = ''
  foregroundColor = color[0]
  backgroundColor = color[1]
  if foregroundColor:
    coloredStr += '\033[38;2;'
    coloredStr += f'{foregroundColor[0]};{foregroundColor[1]};{foregroundColor[2]}m'
  if backgroundColor:
    coloredStr += '\033[48;2;'
    coloredStr += f'{backgroundColor[0]};{backgroundColor[1]};{backgroundColor[2]}m'
  coloredStr += string
  return coloredStr

def addType(string, types): # style e.g. ['bold', 'italic', 'underline']
  styledStr = ''
  for element in types:
    if element == 'bold':
      styledStr += '\033[1m'
    elif element == 'italic':
      styledStr += '\033[3m'
    elif element == 'underline':
      styledStr += '\033[4m'
  styledStr += string
  return styledStr

def calcLength(string):
  pattern = r'(?<=\dm)([^\\]*)(?=\\x1b\[0m)'
  matches = re.findall(pattern, repr(string))
  if matches:
    return len(matches)
  return len(string)

def calcPadding(string, width, padStr=' '):
  pattern = r'(?<=\dm)([^\\]*)(?=\\x1b\[0m)'
  matches = re.findall(pattern, repr(string))
  if matches:
    length = 0
    for match in matches:
      length += len(match)
  else:
    length = len(string)
  padding = padStr * (width - length)
  return padding


def alignLeft(string, width):
  padding = calcPadding(string, width)
  return f'{string}{padding}'


def alignRight(string, width):
  padding = calcPadding(string, width)
  return f'{padding}{string}'


def alignCenter(string, width):
  padding = calcPadding(string, width)
  middleIndex = 0
  if len(padding) % 2 == 0:
    middleIndex = len(padding) / 2
  else:
    middleIndex = (len(padding) - 1) / 2
  middleIndex = int(middleIndex)

  leftPadding = padding[:middleIndex]
  rightPadding = padding[middleIndex:]
  return f'{leftPadding}{string}{rightPadding}'


def wrapString(string, length):
  wrappedString = []
  while True:
    if len(string) > length:
      wrappedString.append(string[:length])
      string = string[length:]
    else:
      wrappedString.append(string)
      break

  return wrappedString

def printError(string):
  print(StyledStr(
    str(string),
    { 'color': [(255, 0, 0), None] }
  ))

def printSuccess(string):
  print(StyledStr(
    str(string),
    { 'color': [(0, 255, 0), None] }
  ))