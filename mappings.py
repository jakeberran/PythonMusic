#mappings.py

import music

def dict2(dictionary): #two way dictionary
  new = {}
  for key in dictionary:
    new[key] = dictionary[key]
    new[dictionary[key]] = key
  return new

def numberPop(strg): #returns the int that is at the end of a string
  num = ''
  for i in range(len(strg)-1, -1, -1):
    if strg[i].isdigit():
      num = strg[i] + num
      strg = strg[:-1]
  return int(num)

pitch_map = dict2({0:'C', 1:'C#', 2:'D', 3:'D#', 4:'E', 5:'F', 6:'F#', 7:'G', 8:'G#', 9:'A', 10:'A#', 11:'B'})

interval_map = dict2({0:'P1', 1:'m2', 2:'M2', 3:'m3', 4:'M3', 5:'P4', 6:'A4', 7:'P5', 8:'m6', 9:'M6', 10:'m7', 11:'M7'})

def toTonalPitch(num, abs=True, midC4=False):
  if isinstance(num, str):
    return num
  if abs:
    octave = num // 12
    if midC4:
      octave -= 1
    return pitch_map[num % 12] + str(octave)

  num = num % 12
  return pitch_map[num]
  
def toNumPitch(pitch, abs=True, midC4=False): #abs just means abs out, can handle either
  if isinstance(pitch, int):
    return pitch
  pitch = toSharps(pitch)
  num = pitch_map[pitch.strip("1234567890")]
  if abs:
    octave = int(pitch.strip("ABCDEFG#b"))
    if midC4:
      octave += 1
    num += 12*octave
  return num
  
def toSharps(tonalPitch):
  x = tonalPitch.replace('Db', 'C#')
  x = x.replace('Eb', 'D#')
  x = x.replace('Gb', 'F#')
  x = x.replace('Ab', 'G#')
  x = x.replace('Bb', 'A#')
  return x

def toTonalInterval(semitones, reduce=False):
  result = interval_map[semitones % 12]
  if not reduce:
    result = result[0] + str(int(result[1])+ 7*(semitones//12))
  return result

def toNumInterval(ivl, reduce=False):
  num = numberPop(ivl)
  addl = 0
  while num > 7:
    addl += 12
    num -= 7
  return interval_map[ivl[0]+str(num)]+addl

def toChordList(quality='maj', root=0):
  if quality[0] in 'CDEFGAB':
    if quality[1] in '#b':
      split = 2
    else:
      split = 1
    root = toNumPitch(quality[:split].strip(' '), False)
    quality = quality[split:].strip(' ')

  chordList = list(chord_map[quality])

  for i in range(len(chordList)):
    chordList[i] += root
  
  return chordList

def toChordName(chord):
  chord = music.Chord(chord).toClosedTertian()
  chordList = chord.pitches
  if isinstance(chordList[0], music.Pitch):
    for i in range(len(chordList)):
      chordList[i] = chordList[i].absolute
  root = min(chordList)
  for i in range(len(chordList)):
    chordList[i] -= root
  try:
    quality = chord_map[tuple(chordList)]
  except:
    max_similars = 0
    for tryList in chord_map:
      if isinstance(tryList, tuple):
        similars = len(set(tryList) & set(chordList))
        if similars > max_similars:
          maybeChord = tryList
    quality = chord_map[maybeChord] + '(?)'

  result = toTonalPitch(root, False) + quality
  return result

def toScaleList(quality='major', center=0):
  if quality[0] in 'CDEFGAB':
    if quality[1] in '#b':
      split = 2
    else:
      split = 1
    center = toNumPitch(quality[:split].strip(' '), False)
    quality = quality[split:].strip(' ')

  scaleList = list(scale_map[quality])

  for i in range(len(scaleList)):
    scaleList[i] += center
  
  return scaleList

def toScaleName(scaleList, center=-1):
  scaleList = [x.pc for x in scaleList]
  if center == -1:
    center = min(scaleList)
  for i in range(len(scaleList)):
    scaleList[i] -= center
  try:
    quality = scale_map[tuple(scaleList)]
  except:
    return 'Unknown Scale'

  result = toTonalPitch(center, False) + ' ' +quality
  return result


scale_map = dict2({'major':(0,2,4,5,7,9,11), 'minor':(0,2,3,5,7,8,10), 'hminor':(0,2,3,5,7,8,11), 'mminor':(0,2,3,5,7,9,11), 'dorian':(0,2,3,5,7,9,10), 'phrygian':(0,1,3,5,7,8,10), 'lydian':(0,2,4,6,7,9,11), 'mixolydian':(0,2,4,5,7,9,10), 'locrian':(0,1,3,5,6,8,10), 'pentatonic':(0,2,4,7,9), 'minpentatonic':(0,3,5,7,10), 'wholetone':(0,2,4,6,8,10), 'oct1':(0,1,3,4,6,7,9,10), 'oct2':(0,2,3,5,6,8,9,11)})

chord_map = dict2({'maj':(0,4,7), 'min':(0,3,7), 'dim':(0,3,6), 'aug':(0,4,8), 'sus':(0,5,7), 'sus2':(0,2,7),'7':(0,4,7,10),'maj7':(0,4,7,11), 'min7':(0,3,7,10), 'dim7':(0,3,6,9), '7b5':(0,3,6,10), 'aug7':(0,4,8,10), 'mM7':(0,3,7,11), 'sus7': (0,5,7,10), 'fr+6':(0,4,6,10), '9':(0,4,7,10,14), 'maj9':(0,4,7,11,14), 'min9':(0,3,7,10,14), '7b9':(0,4,7,10,13),  'maj11':(0, 4, 7, 11, 14, 17), 'maj9#11':(0, 4, 7, 11, 14, 18), 'min11':(0, 3, 7, 10, 14, 17)})

events_dict = {'8':False, '9':True} #this could be completed to include all of them, not just note on or off eventually

meta_dict = {'2f':'end_track', '51':'tempo', '58':'time_sig','59':'key_sig'}

key_sigs = {(-7,0):"Cb major", (-6,0):"Gb major", (-5,0):"Db major", (-4,0):"Ab major", (-3,0):"Eb major", (-2,0):"Bb major", (-1,0):"F major", (0,0):"C major", (1,0):"G major", (2,0):"D major", (3,0):"A major", (4,0):"E major", (5,0):"B major", (6,0):"F# major", (7,0):"C# major", (-7,1):"Ab minor", (-6,1):"Eb minor", (-5,1):"Bb minor", (-4,1):"F minor", (-3,1):"C minor", (-2,1):"G minor", (-1,1):"D minor", (0,1):"A minor", (1,1):"E minor", (2,1):"B minor", (3,1):"F# minor", (4,1):"C# minor", (5,1):"G# minor", (6,1):"D# minor", (7,1):"A# minor"}

'''
print(toChordList('sus7', 6))
print(toChordList('F#min9'))
print(toChordName([1, 5, 9, 11]))
print(toScaleList('D# minor'))
print(toScaleName([1, 3, 5, 7, 9, 11]))
'''