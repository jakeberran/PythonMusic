import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import music, midiwrite, midiread, random, math
import mappings as mp

#these things are not developed right now

def toBeatsView(filename):
  track = midiread.toTrack(filename)
  
  global dt_per_quarter
  #dt_per_quarter = data[12]*256 + data[13]

  global total_time
  total_time = 0

  beatsview = BeatsView()

  return beatsview

class BeatsView:
  def __init__(self, measures=[], time_sig = [4,4]):
    self.measures = measures
    self.time_sig = time_sig

  def addNote(self, note):
    if note.measure > len(self.measures):
      for i in range(len(self.measures), note.measure):
        self.measures.append(Measure([Beat(['-','-','-','-']) for i in range(self.time_sig[0])]))
    self.measures[note.measure-1].beats[note.beat-1].notes[note.partial-1] = note.pitch #%12

  def __str__(self):
    strg = ""
    for a in self.measures:
      strg += "|"
      for b in a.beats:
        last = '-' 
        for c in b.notes:
          '''
          if c == 10:
            c = 't'
          if c == 11:
            c = 'e'
          if c == "-":
            c = last
          strg += str(c)
          last = c
          '''
          try:
            d = mp.toTonalPitch(c, True)
          except:
            d = c
          strg += d
        strg += "."
      strg = strg[:-1]
      strg += '|\n'
    return strg

class Measure:
  def __init__(self, beats=[], key="Keyless"):
    self.beats = beats
    self.key = key

class Beat:
  def __init__(self, notes=[], chord="NC"):
    self.notes = notes
    self.chord = chord
    
class MeasuredMidiEvent:
  def __init__(self, total_time = 0, on=True, pitch=0, velocity=0, time_sig = [4,4], partials=4, dt_per_q = 1000):
    self.total_time = total_time
    total_beat = total_time/dt_per_q #still some wacky stuff here but not urgent
    self.measure = int(total_beat/int(time_sig[0])) + 1
    total_beat -= (self.measure-1)*int(time_sig[0])
    self.beat = int(total_beat)+1
    self.partial = int(partials*(total_beat % 1))+1
    self.on = on
    self.pitch = pitch
    self.velocity = velocity

  def __str__(self):
    try:
      ontext = 'OFF'
      if self.on:
        ontext = 'ON'
      return mp.toTonalPitch(self.pitch) + ' ' + ontext + ' m' + str(self.measure) + ' b' + str(self.beat) + ' p' + str(self.partial)#ontext + ' with velocity ' + str(self.velocity) + ' dt=' + str(self.delta_time) + '\n\t' 
    except:
      return "other midi event"