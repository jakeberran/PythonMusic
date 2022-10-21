#midiwrite.py

#Based on info from
#https://faydoc.tripod.com/formats/mid.htm
#http://www.ccarh.org/courses/253/handout/smf/
#http://midi.teragonaudio.com/tech/midifile.htm

import music

printBArray = False

def write(filename, track=None):
  bl = []

  addheader(bl)

  addtrack(track, bl)

  if printBArray:
    print([hex(i)[2:] for i in bl])

  #finishing things
  barray = bytearray(bl)

  #print(barray)

  outfile = open(filename, 'wb')
  outfile.write(barray)
  outfile.close()

def vt(num): 
  if num == 0:
    return [0]
  outlist = []
  keepgoing = False
  for n in range(3, -1, -1):
    r = num // 2**(7*n)
    num -= r*(2**(7*n))
    if r > 0 or keepgoing:
      keepgoing = True
      if n != 0:
        r += 128
      outlist.append(r)
  
  return outlist

def intToFourBytes(num):
  b_list = []
  for n in range(3, -1, -1):
    r = num//2**(8*n)
    b_list.append(r)
    num -= r*(2**(8*n))
  return b_list

def addon(x, alist=[]): #x is the hex or list of hex to add on
  if isinstance(x, int):
    alist.append(x)
  if isinstance(x, str):
    alist.append(int(x, 16))
  if isinstance(x, list):
    for i in x:
      addon(i, alist)
  return alist

def addheader(alist):
  mthd = ['4d', '54', '68', '64']
  length = ['00', '00', '00', '06']
  format_type = ['00', '00']
  num_tracks = ['00', '01']
  delta_t = ['03', 'e8'] #dt = millisecond

  header = [mthd, length, format_type, num_tracks, delta_t]

  alist = addon(header, alist)
  return alist

def addevent(event, current_t=0, alist=[]): #want to be able to pass in some event object
  #for the note on note off probably
  t = event.t
  dt = int(1000*(t - current_t))
  current_t = t
  on = {True:'90', False:'80'}[event.on]
  #print(dt, vt(dt))
  event_list = vt(dt) + [on, event.pitch, event.velocity]
  addon(event_list, alist)
  return alist, current_t

def addtrack(track=music.Track(), alist=[]):
  mtrk = ['4d', '54', '72', '6b']
  #tempo = ['ff', '51', '03'] + vt(1000000) #60 bpm, 1 million microseconds per quarter note
  timesig = ['ff', '58', '04', 1, 2, 1, 32] #32 32nd notes per quarter, 1/4 time to be based on seconds
  
  midi_events = []
  current_t = 0
  for event in track.events:
    if isinstance(event, music.MidiEvent):
      result = addevent(event, current_t, midi_events)
      midi_events = result[0]
      current_t = result[1]
  end_track = ['ff', '2f', '00']

  afterlength = addon(timesig + midi_events + end_track)
  #print(afterlength)
  length = intToFourBytes(len(afterlength))
  
  #print(length)
  track = mtrk + length + afterlength

  alist = addon(track, alist)
  return alist