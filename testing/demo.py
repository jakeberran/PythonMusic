#demo.py

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import music, midiwrite, midiread, random, math
import mappings as mp

#####
#DEMO STARTS HERE
#####

#import a midi file as a Track object from music.py, which basically consist of a list of Note objects
track = midiread.toTrack('scale.mid')
print(track) #lists notes, their start/end times, duration, and velocity

#working with the Pitch and Interval classes, a little clunky because Notes have ints as their pitch
pitch1 = music.Pitch(track.notes[0].pitch) # C#5
print(pitch1.invert(61)) #inverts over C#5 to get D5, doesn't actually change pitch1

pitch2 = music.Pitch(79) #A6

interval12 = pitch1.intervalWith(pitch2)
print(interval12)

octx3 = interval12.diminish(7).multiply(3) #shorten the interval by a P5 and multiply it by 3 to get 3 octave interval
print(octx3) 

print(pitch1.transpose(octx3.absolute)) #i still need to expand a lot of the methods so they can take numbers or Intervals, Pitches, etc.

print()

#make a Chord of four stacked fourths (five notes) (a fun method!)
fourth = music.Interval('P4')
chord1 = fourth.toChord(4, 5)
print(chord1)
chord1closed = chord1.toClosedTertian() #gets it into stacked thirds (this is my favorite function, allows for translating to chord symbols so one could record some midi and then make it spit out the chord symbols for e.g. a guitarist to jam)
print(chord1closed)
#the chord symbols aren't always right, especially for incomplete chords, so I will fix that in the future

#Scale class
print()
scale1 = music.Scale([x.pitch for x in track.notes])
print(scale1) #prints the scale it thinks that original Track (just a C major scale) is in
print()

#this next one is four three note chords, so we will demonstrate some Track methods by just printing the chord names! could also be outputted to midi
def printChords(track):
  for i in range(len(track.notes)//3):
    print(music.Chord([x.pitch for x in track.notes[3*i:3*i+3]]))

track2 = midiread.toTrack('chords.mid')

#for some reason these modify track2 instead of just returning the new track, so I don't know why but the methods do work.
print()
print(track2)
printChords(track2)
print()
printChords(track2.invert(0)) #inverts over C5
print()
printChords(track2.transpose(7)) #transposes that up a perfect fifth
print()
printChords(track2.retrograde()) #takes the track in retrograde


#finally, let's output a midi file with the new track2!
midiwrite.write('newchords.mid', track2)