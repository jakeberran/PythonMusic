#particles.py

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import music, midiwrite, random, math

filename = 'particles.mid'

def randList(lst):
  return lst[random.randrange(len(lst))]

def randITrgl():
  r = random.random()
  if r > 0.5:
    r = 0.5*(1-r)+r**2
  else:
    r = r**0.5-0.21*(2*r)
  return r

def randRTrgl(order=1):
  r = random.random()**(1/(order+1))
  return r

def randLTrgl(order = 1):
  r = random.random()**(order+1)
  return r

def shape1(pitches, start, end, pitches2=0, start2=0):
  notes = []
  dynamic_peak = 17

  for i in range((end-start)*6): #*3
    r = randITrgl()
    
    nstart = start+r*(end-start)
    
    if pitches2 == 0 or nstart < start2:
      npitch = pitches[random.randrange(len(pitches))]
    else:
      npitch = pitches2[random.randrange(len(pitches2))]
    
    ndur = 0.5
    
    if nstart < dynamic_peak:
      nvel = 100*(nstart-start)/(dynamic_peak-start)
    else:
      nvel = 100*(1-(nstart-dynamic_peak)/(end-dynamic_peak)) #17 to 20 maps to 1 to 0
    
    nvel = nvel // 2 + 50

    nart = 0.25+0.75*r
    
    note = music.Note(npitch, nstart, ndur, nvel, nart)
  
    notes.append(note)

  return music.Track(notes)

def shape2(pitches, start, end, cresc=True, pitches2=0, start2=0):
  notes = []

  for i in range((end-start)*6): #*3
    r = randRTrgl()
    
    nstart = start+r*(end-start)

    if pitches2 == 0 or nstart < start2:
      npitch = pitches[random.randrange(len(pitches))]
    else:
      npitch = pitches2[random.randrange(len(pitches2))]
    
    ndur = 0.5
    
    if cresc:
      nvel = 50+50*r
    else:
      nvel = 100-50*r

    nvel = int(nvel)

    nart = 1 - 0.75*r
    
    note = music.Note(npitch, nstart, ndur, nvel, nart)
  
    notes.append(note)

  return music.Track(notes)

def shape3(pitches, start, end):
  notes = []

  for i in range(int((end-start)*1.5)): #*3
    r = randITrgl()
    
    scale_length = int(len(pitches)*2*abs(r-0.5))+1
    if scale_length == 0:
      scale_length = 1

    if r < 0.5: #ascending
      start_i = random.randrange(0, len(pitches)-scale_length+1)
      npitches = pitches[start_i:start_i+scale_length]
    else:
      start_i = random.randrange(scale_length-1, len(pitches))
      npitches = [pitches[j] for j in range(start_i, start_i-scale_length, -1)]

    nstart = start+r*(end-start)
    
    ndur = random.randrange(10, 30, 5)/150
    
    nvel = 80

    nart = 1
    
    for i in range(len(npitches)):
      notes.append(music.Note(npitches[i], nstart+i*ndur, ndur, nvel, nart))

  return music.Track(notes)

def shape4(start=81, end=109, red_scale=[0, 1, 3, 5, 7, 8, 10], center=73, amplitude=18, period=14, width=12, start_high=True, dynamic_type=1):
  notes = []

  b = 2*math.pi/period
  length = end-start
  for i in range((length)*11):
    rel_start = random.random()*(length)
    r = rel_start/(length)
    nstart = rel_start + start

    nrange_center = int(amplitude*+math.cos(b*rel_start)+center) #default to cos, starts at top
    if not start_high:
      nrange_center = 2*center - nrange_center #flips around center
    nrange = (nrange_center - width//2, nrange_center + width//2)

    while True:
      npitch = random.randrange(nrange[0], nrange[1])
      if npitch % 12 in red_scale:
        break


    if dynamic_type == 1:
      nvel = 80
      if r > 0.5:
        nvel = r*(-240)+200
        if r > 0.75:
          nvel = r*240-160
    elif dynamic_type == 2:
      nvel = 20
      if r > 0.25:
        nvel = min(80, r*240-40)
        
    ndur = 0.25
    nart = 1
    
    notes.append(music.Note(npitch, nstart, ndur, nvel, nart))
  
  return music.Track(notes)

def shape5(red_scale, start_range, start=109, splits=[110,114,119,121], end=122):
  notes = []
  
  length = end-start

  ranges = [[list(range(start_range[0], start_range[1]+1))]] #extra brackets so nesting is consistent
  for i in range(len(splits)):
    newlength = int(len(ranges[i][0])*2/3)
    nextrange = []

    for prevrange in ranges[i]: #each list-range-set thing in the last open
      highstart = max(prevrange)+1
      lowstart = min(prevrange)-1
      nextrange.append(list(range(highstart, highstart + newlength + 1)))
      nextrange.append(list(range(lowstart, lowstart - newlength - 1, -1)))
    ranges.append(nextrange)

  

  pitches = []
  for i in range(len(ranges)):
    pitchesi = []
    for j in range(len(ranges[i])):
      for k in range(len(ranges[i][j])):
        pitchesi.append(ranges[i][j][k])
    pitches.append(pitchesi)

  #print(ranges)
  #print(pitches)

  #pitches[i] is now the ith set of pitches, to be used after spliti

  nextpitches = [] #for shape6

  for i in range(length*15): #create that many notes
    nstart = start+random.random()*length

    s = [start]+splits+[end] #splits including the start and end
    for i in range(len(s)-1):
      if nstart > s[i] and nstart < s[i+1]:
        while True:
          npitch = randList(pitches[i])
          if npitch % 12 in red_scale:
            break

    nvel = 30
    proximity = min([abs(nstart-split) for split in s])
    if proximity < 1:
      p = 1-proximity #so 1 at the high points, 0 at the low
      nvel = 30 + 70*p

    ndur = 0.25
    nart = 1
  
    notes.append(music.Note(npitch, nstart, ndur, nvel, nart))

    if nstart > 120:
      nextpitches.append(npitch)
  
  return music.Track(notes), nextpitches

def shape6(pitches, start, end):
  notes = []

  lowest = min(pitches)
  pitches_range = max(pitches) - lowest
  for i in range((end-start)*6): #*3
    r = randLTrgl()
    
    nstart = start+r*(end-start)

    while True:
      npitch = randList(pitches)
      if npitch - lowest < pitches_range*(1-r):
        break
    
    ndur = 0.5 - 0.4*r
    
    nvel = 100 - 100*r

    nart = 1
    
    note = music.Note(npitch, nstart, ndur, nvel, nart)
  
    notes.append(note)

  return music.Track(notes)


def shape7(start=125, end=160, avg_density = 35, order = 3):
  notes = []

  length = end - start
  for i in range(length*avg_density):
    nstart = start + randRTrgl(order)*length
    npitch = random.randrange(128)
    ndur = 0.05
    nvel = 20 + 80*random.random()
    nart = 1

    notes.append(music.Note(npitch, nstart, ndur, nvel, nart))

  return music.Track(notes)

def shape8(start = 160, end=187, poss_pitches = [[2, 4, 7, 9, 11], [1, 3, 4, 7, 10], [0, 1, 3, 4, 6, 7, 9, 10]]):
  notes = []

  length = end-start
  for i in range(length*6):
    a = random.random()
    if a < 0.5:
      b = 0
    elif a < 0.75:
      b = 1
    else:
      b = 2
    pitches = poss_pitches[b]
    
    r = random.random()

    nstart = start + length*r

    num_notes = int(7*(1-r)) #actually is one less than the number of notes
    lowest = randList(pitches) + 12*random.randrange(2, 7)
    chord = [lowest]
    trypitch = lowest
    while num_notes > 0:
      trypitch += 1
      if trypitch % 12 in pitches:
        chord.append(trypitch)
        num_notes -= 1

    nvel = 70
    ndur = 0.25
    nart = 1

    for npitch in chord:
      notes.append(music.Note(npitch, nstart, ndur, nvel, nart))

  return music.Track(notes)


def shape9(splits=[190, 193, 196, 199, 202, 205, 212, 220], poss_pitches = [[0, 2, 4, 5, 7, 9, 11], [0, 1, 3, 5, 7, 8, 10]]):
  notes = []

  length = splits[-1]-splits[0]
  start = splits[0]
  for i in range(length*4):
    a = random.random()
    if a < 0.5:
      b = 0
    else:
      b = 1
    pitches = poss_pitches[b]
    
    r = random.random()

    allstart = start + length*r

    num_notes = int(7*r) #number of addl notes each direction
    middle = randList(pitches) + 12*random.randrange(int(4-3*r), int(5+4*r)+1)
    chord = [middle]
    
    trypitch = middle #goes above
    left = num_notes
    while left > 0:
      trypitch += 1
      if trypitch % 12 in pitches:
        chord.append(trypitch)
        left -= 1
    
    trypitch = middle #goes below
    left = num_notes
    while left > 0:
      trypitch -= 1
      if trypitch % 12 in pitches:
        chord.append(trypitch)
        left -= 1

    chord.sort()

    ndur = 0.05+0.07*random.random()
    nart = 1
    allvel = 30+90*r

    for i in range(len(chord)):
      distance = abs(i-num_notes)
      nstart = allstart + ndur*(distance)
      npitch = chord[i]
      if distance != 0:
        nvel = allvel-(allvel-20)*(distance/num_notes)
      else:
        nvel = allvel

      notes.append(music.Note(npitch, nstart, ndur, nvel, nart))

  return music.Track(notes)

def shape10(splits=[220, 227, 230, 233], direction_split=61):
  notes = []

  length = splits[-1] - splits[0]
  for i in range(length*10):
    r = randRTrgl(2)
    
    start1 = splits[0] + r*length

    for i in range(len(splits)):
      if start1 > splits[i]:
        num_notes = len(splits)-1 - i #actual number of notes this time
    
    pitch1 = random.randrange(int(r*direction_split), int(127-r*(127-direction_split)))
    if pitch1 > direction_split:
      step = -1
    else:
      step = 1
    
    ndur = 0.05+0.07*random.random()
    nvel = 100

    counter = 0
    for npitch in range(pitch1, pitch1 + step*num_notes, step):
      nstart = start1 + counter*ndur
      notes.append(music.Note(npitch, nstart, ndur, nvel))
      counter += 1
  
  return music.Track(notes)


def shape11(pitch=61, start=233, end=240):
  notes = [] #hmm i feel like functional programming would be nice here, or maybe i am just not seeing something. a lot of repetition. i guess i could use exec or eval or something
  length = end-start
  for i in range(10*length):
    r = randLTrgl(2)

    nstart = start + r*length
    nvel = 127-127*r
    npitch = pitch
    ndur = 0.05+0.07*r
    nart = 1
    notes.append(music.Note(npitch, nstart, ndur, nvel, nart))

  return music.Track(notes)




#making each section (based on time)


part1 = music.Track([])

part1.insert(shape1([37, 44, 49], 0, 20))
part1.insert(shape1([52, 57], 4, 22, [53, 55], 12))
part1.insert(shape1([71, 75, 68], 8, 23))
part1.insert(shape1([86, 93, 98, 102] , 15, 25))
part1.cutSilence()

part2 = music.Track([]) #for some reason i need the [] or it adds notes from track1?!

part2.insert(shape2([39, 46, 51], 30, 44, False))
part2.insert(shape2([52, 59], 34, 47, False, [54, 56], 41))
part2.insert(shape2([62, 69, 70, 77], 38, 49, True))
part2.insert(shape2([81, 84, 91], 44, 52, True))

part3 = music.Track([])


part3.insert(shape3([56, 58, 59, 62, 66, 67], 55, 78))
part3.insert(shape3([32, 34, 35, 38, 42, 43], 68, 74))
part3.insert(shape3([44, 46, 47, 50, 54, 55], 62, 76))
part3.insert(shape3([68, 70, 71, 74, 78, 79], 62, 76))
part3.insert(shape3([80, 82, 83, 86, 90, 91], 68, 74))


part4 = music.Track([])

part4.insert(shape4())
part4.insert(shape4(90, 109, [1, 3, 5, 6, 8, 10, 11], 59, 18, 19, 12, False, 2))


part5 = music.Track([])

x = shape5([0, 1, 3, 5, 7, 8, 10], [85, 97])
part5.insert(x[0])
y = shape5([1, 3, 5, 6, 8, 10, 11], [35, 47])
part5.insert(y[0])
nextpitches = x[1]+y[1]

part6 = music.Track([])

part6.insert(shape6(nextpitches, 122, 130))

part7 = shape7()

part8 = shape8()

part9 = shape9()
part10 = shape10()
part11 = shape11()
#putting them all into the final track

final = music.Track([])

parts = [part1, part2, part3, part4, part5, part6, part7, part8, part9, part10, part11]
for part in parts:
  try:
    final.insert(part)
  except:
    pass


#writing to the filename at top
midiwrite.write(filename, final)