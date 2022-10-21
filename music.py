#music.py

import itertools
import mappings as mp
import random
import math

class Pitch:
  def __init__(self, absolute):
    if isinstance(absolute, str):
      absolute = mp.toNumPitch(absolute)
    self.absolute = absolute
    self.pc = absolute % 12
    if absolute < 0:
      self.absolute = absolute % 12

  def __gt__(self, other):
    return self.absolute > other.absolute
  def __lt__(self, other):
    return self.absolute < other.absolute
  def __ge__(self, other):
    return self.absolute >= other.absolute
  def __le__(self, other):
    return self.absolute <= other.absolute
  def __eq__(self, other):
    return self.absolute == other.absolute

  def __add__(self, other):
    return Pitch(self.absolute+other.absolute)

  def __sub__(self, other):
    return Pitch(self.absolute - other.absolute)

  def __str__(self):
    return mp.toTonalPitch(self.absolute, True) + ', reduced pc' + str(self.pc)

  def intervalWith(self, other):
    return Interval(self.absolute - other.absolute)

  def invert(self, axis=0, absolute=True): #idk why absolute would be false, it will just return a pitch 
    if isinstance(axis, Pitch):
      axis = axis.absolute
    if absolute:
      return Pitch(2*axis - self.absolute)

  def transpose(self, interval):
    return Pitch(self.absolute + interval)

class Interval:
  def __init__(self, pitch1, pitch2=0): #if only one argument, pitch1 is just the number of semitones
    if isinstance(pitch1, Pitch):
      pitch1 = pitch1.absolute
    if isinstance(pitch2, Pitch):
      pitch2 = pitch2.absolute
    if isinstance(pitch1, str):
      pitch1 = mp.toNumInterval(pitch1)
    self.total = int(pitch2) - int(pitch1)
    if pitch2 == 0:
      self.total = -1*self.total
    self.absolute = abs(int(pitch1) - int(pitch2)) #in case float?
    self.ic = self.absolute % 12
    self.reduced = min(self.ic, 12-self.ic)
  
  def __str__(self):
    return "Interval {}, ic{}, reduced ic{} ".format(self.absolute, self.ic, self.reduced) + "({} or {})".format(mp.toTonalInterval(self.absolute, False), mp.toTonalInterval(self.absolute, True)) #is there an __int__ override for classes?

  def augment(self, semitones = 1):
    return Interval(self.absolute+semitones)

  def diminish(self, semitones = 1):
    return Interval(self.absolute-semitones)

  def inversion(self, total=12): #inversion of 12 will be 0, but 13 will be 11 again.
    if total % 12 == 0 and self.absolute % 12 == 0:
      return Interval[total - 12]
    return Interval(total - self.ic)

  def multiply(self, factor=1):
    return Interval(self.absolute*factor)

  def toChord(self, num, rt=0): #num is the number of consecutive (this interval)s that the chord is made of
    return Chord([self.absolute]*num, True, rt)

class OrderedPitchSet:
  def __init__(self, intervals_or_pitches = [0], initWithIntervals=False, rt=0): #default root note of 0
    if initWithIntervals:
      intervals = intervals_or_pitches
      if isinstance(intervals[0], Interval):
        intervals = [x.total for x in intervals]
      self.intervals = intervals
      self.rt = rt
      self.updatePitches()
      
    else:
      pitches = intervals_or_pitches
      if isinstance(pitches[0], Pitch):
        pitches = [x.absolute for x in pitches]
      self.pitches = [Pitch(i) for i in pitches]
      self.updateIntervals()
      self.rt = pitches[0]
  
  def print2(self):
    strg = ''
    minpitch = min([x.absolute for x in self.pitches])
    for pitch in self.pitches:
      strg += mp.toTonalPitch(pitch.pc)
      for i in range((pitch.absolute - minpitch - minpitch%12)//12):
        strg += "'"
      strg += ','
    strg = strg[:-1]
    return strg

  def __str__(self):
    strg = ''
    for pitch in self.pitches:
      strg += mp.toTonalPitch(pitch.absolute, True, False) + ','
    strg = strg[:-1]
    return strg
    

  def updateIntervals(self):
    self.intervals = [Interval(self.pitches[i], self.pitches[i+1]) for i in range(0, len(self.pitches)-1)]

  def updatePitches(self):
    self.pitches = [Pitch(self.rt + sum(self.intervals[:i])) for i in range(len(self.intervals)+1)]

  def invert(self, axis):
    newPitches = []
    for pitch in self.pitches:
      newPitches.append(pitch.invert(axis))
    return OrderedPitchSet(newPitches)
  
  def transpose(self, interval=0):
    return OrderedPitchSet(self.intervals, True, self.rt+interval)

  def retrograde(self):
    newPitches = []
    for i in range(len(self.pitches)-1, -1, -1):
      newPitches.append(self.pitches[i])
    return OrderedPitchSet(newPitches)

class UnorderedPitchSet(OrderedPitchSet):
  def __init__(self, intervals_or_pitches = [0], initWithIntervals=False, rt=0):
    if isinstance(intervals_or_pitches, OrderedPitchSet):
      pitches = intervals_or_pitches.pitches
      super().__init__(pitches, False)
    else:
      super().__init__(intervals_or_pitches, initWithIntervals, rt)
    #print([x.absolute for x in self.pitches])
    ##self.pitches = list(set(self.pitches))#.sort(key = lambda x: x.absolute)
    #print(self.pitches)
    pitches = self.pitches
    self.intervals = [Interval(pitches[i], pitches[i+1]) for i in range(0, len(pitches)-1)] #for some reason self.pitches is None, fix that

  def union(self, other, absolute=True): #maybe not have this as a method, and accept an arbitrary number?
    union = []
    for pitch in self.pitches + other.pitches:
      if pitch not in union:
        if absolute:
          union.append(Pitch(pitch).absolute)
        else:
          union.append(Pitch(pitch).pc)
    return UnorderedPitchSet(union)
  
  def intersection(self, other, absolute=True): #see below
    if isinstance(self, Scale):
      self = UnorderedPitchSet([Pitch(i) for i in self.allpitches])
    if isinstance(other, Scale):
      #print(other.allpitches)
      other = UnorderedPitchSet([Pitch(i) for i in other.allpitches])
    
    intersection = []
    for pitch in self.pitches:
      if pitch.absolute in [x.absolute for x in other.pitches]:
        if absolute:
          intersection.append(pitch.absolute)
        else:
          intersection.append(pitch.pc)
    return UnorderedPitchSet(intersection)
  
  def randPitch(self):
    r = random.randrange(0, len(self.pitches))
    return self.pitches[r]

def pitchRange(a, b=0):
  pitches = []
  if a > b:
    a, b = b, a
  for i in range(a, b+1):
    pitches.append(i)
  return UnorderedPitchSet(pitches)

class Chord(UnorderedPitchSet): 
  def __init__(self, intervals_or_pitches = [0], initWithIntervals=False, rt=0):
    super().__init__(intervals_or_pitches, initWithIntervals, rt)

  def __str__(self):
    strg = ''
    for pitch in self.pitches:
      strg += mp.toTonalPitch(pitch.pc, False)
      for i in range((pitch.absolute - Pitch(self.pitches[0].absolute - self.pitches[0].absolute%12).absolute)//12):
        strg += "'"
      strg += ','
    strg = strg[:-1]
    strg2 = mp.toChordName(self.pitches)
    return strg + ' = ' + strg2

  def toQuality(self): #maybe have a mapping between lists and chord qualities? or try to program
    tertian = self.toClosedTertian()
    #how to deal with suspended chords, etc.? I need a little more than the to tertian. maybe a toSmartVoicing?? what would smart do?
    return "nothing here yet"

  def toClosedTertian(self): #should it return, or modify the chord?
    chord = Chord(self.pitches)
    max_thirds = 0
    permList = list(itertools.permutations(chord.crush().pitches))
    permNums = [[x.absolute for x in perm] for perm in permList]
    for perm in permNums: #gets just the pitches in the chord, does every order
      #print('perm:' , perm)
      #input()
      thisPerm = list(perm) #so it's mutable
      for i in range(1,len(thisPerm)): #puts the temp chord in increasing order
        while thisPerm[i] < thisPerm[i-1]:
          thisPerm[i] += 12
      tempChord = Chord(thisPerm) #make a chord with those pitches

      #print(tempChord)
      #print(self.crush())

      thirds = 0
      for interval in tempChord.intervals:
        if interval.absolute in [3,4]:
          thirds += 1

      if thirds > max_thirds:
        max_thirds = thirds
        chord = tempChord
    return chord

  def toScale(self):
    return Scale([pitch.reduced for pitch in self.pitches])

  def crush(self): #same as toScale but returns chord
    chord = []
    for pitch in self.pitches:
      pitch = pitch.pc #effectively mod12s, but satisfying. should i then move the first pitch to the last position until the first one in the chord is the same as the original chord?
      if pitch not in chord:
        chord.append(pitch)
      chord.sort()
    return Chord(chord)
  
  def toInversion(self, degree=1): #makes a closed position using toTertian
    chord = self.toTertian()
    print(degree%len(self.pitches))
    for i in range(degree % len(self.pitches)): #so that it doesn't go up and up
      print(chord.pitches[i])
      chord.pitches[i] += 12
      print(chord.pitches[i])
    return chord

class Scale(UnorderedPitchSet):
  def __init__(self, pitch=[], quality='major'):
    if isinstance(pitch, str):
      pitches = mp.toScaleList(pitch)
      pitches = [Pitch(x) for x in pitches]
    elif isinstance(pitch, int):
      pitches = mp.toScaleList(quality, pitch)
      pitches = [Pitch(x) for x in pitches]
    elif isinstance(pitch, list):
      pitches = [Pitch(x) for x in pitch]
    elif isinstance(pitch, UnorderedPitchSet):
      pitches = pitch.pitches
    self.pitches = []
    for pitch in pitches:
      if pitch.pc not in [x.pc for x in self.pitches]:
        self.pitches.append(pitch)
    self.degrees = []
    for pitch in self.pitches:
      self.degrees.append(pitch.pc)
    self.length = len(self.pitches)
    self.allpitches = []
    for octave in range(11):
      self.allpitches += [12*octave+pc for pc in self.degrees]
    self.allpitches.sort()
    for i in range(len(self.allpitches)):
      if self.allpitches[i] > 127:
        self.allpitches = self.allpitches[:i]
        break

  def __str__(self):
    return mp.toScaleName(self.pitches)

def scaleRange(scale, a, b):
  return (pitchRange(a, b).intersection(Scale(scale)))
  
class Melody(OrderedPitchSet):
  def __init__(self, intervals_or_pitches=[], durations=[], initWithIntervals=False, rt=0):
    super().__init__(intervals_or_pitches, initWithIntervals, rt)
    self.notes = [Note(self.pitches[0], 0, durations[0])]
    t = durations[0]
    for i in range(1, len(durations)):
      self.notes.append(Note(self.pitches[i], t, durations[i]))
      t += durations[i]
  
  def __str__(self):
    strg = ''
    for note in self.notes:
      strg += str(note.pitch) + ': ' + str(note.duration) + '\n'
    return strg

class Note():
  def __init__(self, pitch=60, start=0, duration=0, velocity=100, articulation = 1):
    if isinstance(pitch, Pitch):
      pitch = pitch.absolute
    self.pitch = int(pitch)
    self.start = round(start, 3)
    self.duration = round(duration, 3)
    self.articulation = round(articulation, 3)
    self.end = round(start + duration*articulation,3)
    self.velocity = int(velocity)

  def __str__(self):
    strg = mp.toTonalPitch(self.pitch) + ', t=' + str(self.start) + ', e=' + str(self.end)+ ', d=' + str(self.end - self.start) + ', v='+str(self.velocity)+'\n'
    return strg

class MidiEvent():
  def __init__(self, on, pitch, t, velocity=100):
    self.on = on
    self.pitch = int(pitch)
    self.t = t #assumes in seconds, so i will convert it in the write and read things
    self.velocity = int(velocity)
  
  def __str__(self):
    strg = mp.toTonalPitch(self.pitch)
    if self.on:
      strg += ' ON '
    else:
      strg += ' OFF '
    strg += 't='+str(self.t)+' v='+str(self.velocity)
    return strg

class MetaEvent:
  def __init__(self, which=None, value=None, total_time = 0):
    self.which = which
    self.value = value #make sure time signatures are like [4,4]
    self.t = total_time
  
  def __str__(self):
    strg = ''
    strg += str(self.which) 
    if self.value:
      strg += ': ' + str(self.value)
    strg += ', t='+str(self.t)
    return strg
  
class Track():
  def __init__(self, notes=list(), metas=list()):
    self.notes = notes
    self.metas = metas #list of meta events, will handle later
    self.midiProcess()

  def __str__(self):
    strg = ''
    for note in self.notes:
      strg += str(note)
    return strg

  def midiProcess(self):
    self.notes.sort(key=lambda x: x.start)
    self.events = [] #each entry will have format [on?, pitch, time]
    for note in self.notes:
      self.events.append(MidiEvent(True, note.pitch, note.start, note.velocity))
      self.events.append(MidiEvent(False, note.pitch, note.end, note.velocity))
    for meta in self.metas:
      self.events.append(meta)
    self.events.sort(key=lambda x: x.t) #maybe indent this f it bugs?

  def pythonProcess(self): #probably dont weant to do this unless it's an incoming midi file. also this usually makes a bunch of zero length notes and the lengths are off in general. but i don't really need this part right now?
    noteEvents = []

    self.events.sort(key=lambda x: x.t)

    #print(self.events)

    for event in self.events:
      if isinstance(event, MidiEvent):
        noteEvents.append(event)
      elif isinstance(event, MetaEvent):
        self.metas.append(event)
    
    eventsByNote = [[]]*128

    for event in noteEvents:
      pitch = event.pitch
      temp = eventsByNote[event.pitch]
      eventsByNote[event.pitch] = temp + [event] #matrix of events for each note

    #print(eventsByNote)

    for i in range(128):
      eventsi = eventsByNote[i] #events of the ith note
      ons = []
      offs = []
      for event in eventsi:
        if event.on:
          ons.append(event)
        else:
          offs.append(event)
      for i in range(min(len(ons), len(offs))):
        pitch = ons[i].pitch
        start = ons[i].t
        duration = offs[i].t - start
        velocity = ons[i].velocity
        articulation = 1
        self.notes.append(Note(pitch, start, duration, velocity, articulation))
    self.notes.sort(key = lambda x: x.start)



  def addNotes(self, notes=[]):
    if isinstance(notes, Note):
      if notes.pitch >= 0 and notes.pitch < 128:
        self.notes.append(notes)
    elif isinstance(notes, list):
      for note in notes:
        if note.pitch >= 0 and note.pitch < 128:
          self.notes.append(note)
    self.midiProcess()

  def addMetas(self, metas=[]):
    if isinstance(metas, MetaEvent):
      self.metas.append(metas)
    elif isinstance(metas, list):
      for meta in metas:
        self.metas.append(meta)
    self.midiProcess()

  def cutSilence(self):
    min_start_t = min([note.start for note in self.notes])
    for i in range(len(self.notes)):
      self.notes[i].start -= min_start_t
      self.notes[i].end -= min_start_t
    self.midiProcess()

  def insert(self, tracks, t=0):
    if isinstance(tracks, list):
      for track in tracks:
        self.insert(track)  
    else:
      for note in tracks.notes:
        newNote = note
        newNote.start += t
        newNote.end += t
        self.notes.append(newNote)
      self.midiProcess()

  def transpose(self, interval=Interval(0)):
    new = Track(self.notes, self.metas)
    if isinstance(interval, Interval):
      x = interval.total
    else:
      x = interval
    for note in new.notes:
      note.pitch += x
    new.midiProcess()
    return new
  
  def stretch(self, factor=1):
    new = Track(self.notes, self.metas)
    for note in new.notes:
      note = Note(note.pitch, note.start*factor, note.duration*factor, note.velocity, note.articulation)
    new.midiProcess()
    return new
  
  def retrograde(self):
    new = Track(self.notes, self.metas)
    max_end_t = max([note.end for note in new.notes])
    for note in new.notes:
      start = note.start
      end = note.end
      note.start = max_end_t - end
      note.end = max_end_t - start
    new.notes.sort(key = lambda x:x.pitch)
    new.midiProcess()
    return new

  def invert(self, axis = 0):
    new = Track(self.notes, self.metas)
    if axis == 0:
      axis = new.notes[0].pitch
    for note in new.notes:
      note.pitch = 2*axis - note.pitch
    new.midiProcess()
    return new