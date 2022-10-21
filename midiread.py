#midiread.py

#Based on info from
#https://faydoc.tripod.com/formats/mid.htm
#http://www.ccarh.org/courses/253/handout/smf/
#http://midi.teragonaudio.com/tech/midifile.htm

import mappings as mp
import music

testing = False

#convert a midi into the track class
def toTrack(filename, start_t = 0):
  f = open(filename, 'rb')

  data = f.read() #creates bytes object, immutable array of ints

  f.close()

  if testing:
    print('MIDI file in hex: ',[byte(i, data) for i in range(len(data))])
    print()
  
  cursor = 22

  total_time = int(start_t*1000) #in case of offset, also converts to ms

  track = music.Track([])

  while True:
    y = processEvent(cursor, data, track, total_time)
    cursor = y[0]
    track = y[1]
    total_time = y[2]
    
    if cursor == 'stop': #or cursor > 100
      break
  
  track.pythonProcess()
  
  return track

#individual event processing things:
def byte(pos, data, to_int=False):
  try:
    if to_int:
      return data[pos]
    return hex(data[pos])[2:]
  except:
    pass

def processEvent(cursor, data, track, total_time):
  init_cursor = cursor
  
  try:
    done_test = data[cursor] #to test if cursor is in a valid spot
  except:
    if testing:
      print("Done")
    return 'stop', track, total_time

  if [byte(i, data) for i in range(cursor, cursor+4)] == ['4d', '54', '72', '6b']:
    if testing:
      print("MTrk Here")
    cursor += 8

    if testing:
      print([byte(i, data) for i in range(init_cursor, cursor)])
      print()
    return cursor, track, total_time

  command = byte(cursor, data) #gets the current byte
  
  if command == 'ff': #tests if its a meta event
    x = music.MetaEvent()
    
    command2 = byte(cursor+1, data)
    try:
      x.which = mp.meta_dict[command2]
    except:
      if testing:
        print("Some other meta")
      cursor += data[cursor+2] + 3 #based on the length number in the meta event
      
      if testing:
        print([byte(i, data) for i in range(init_cursor, cursor)])
        print()
      return cursor, track, total_time
    
    if x.which == "time_sig":
      x.value = [data[cursor+3], int(2**data[cursor+4])]
      cursor += 7
    elif x.which == "key_sig":
      x.value = mp.key_sigs[(data[cursor+3],data[cursor+4])]
      cursor += 5
    elif x.which == "end_track":
      x.value = None
      cursor += 3
    elif x.which == "tempo":
      micros_per_q = 65536*data[cursor+3] + 256*data[cursor+4] + data[cursor+5]
      x.value = int(60*micros_per_q/1000000)
      cursor += 6
    x.t = total_time

    track.metas.append(x)

    if testing:
      print(x)

  else: #assumes it's a midi event
    delta_time = 0
    for i in range(cursor,cursor+4): #determining the delta t of this event
      if data[i] < 128: #then that byte is the last byte of the number
        last_byte = i
        break
    for j in range(cursor,last_byte): #now iterate over the bytes that comprise the delta t, the i one is after loop
      delta_time += (128**(last_byte-j))*(data[j] - 128)
    delta_time += data[last_byte]
    
    total_time += delta_time
    #print(cursor)
    cursor = last_byte+1 #sets at the starting position for the event (excluding delta_time)
    
    command = byte(cursor, data)

    #print(command, delta_time)

    if command[0] not in mp.events_dict:
      if testing:
        print("Some other midi event")
      if command[0] in ['c', 'd']:
        cursor += 4
      else:
        cursor += 3

      if testing:
        print([byte(i, data) for i in range(init_cursor, cursor)])
        print()
      return cursor, track, total_time
    
    try:
      x = music.MidiEvent(mp.events_dict[command[0]], data[cursor+1], total_time/1000, data[cursor+2]) #now assumes its a note on or off
    except:
      pass

    track.events.append(x)

    if testing:
      print(x)
    
    #print(cursor)
    cursor += 3
    
  
  if testing:
    print([byte(i, data) for i in range(init_cursor, cursor)])
    print()
  return cursor, track, total_time