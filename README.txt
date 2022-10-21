PythonMusic Library
Jake Berran
Last Updated: 05/07/21

Hello! This is the PythonMusic library, or whatever it should be called since I am a beginner programmer. It has many functions to work with music and MIDI files. It's very much in progress, but still at a point where people can use it if they wish.

Here is a general overview of the folders and files:

- testing/demo.py -
  This is probably the best place to go for seeing the library in action. It includes importing MIDI, manipulating musical objects, and exporting MIDI. It uses scale.mid and chords.mid, and outputs newchords.mid if run.

- particles -
  An example of programming a MIDI file based on a score of indeterminate music. I coded a "performance" of Particles (or rather a performance template with randomness) in particles.py, which I wrote for music theory class. Not very many of the music.py classes are used, but it shows a lot of potential for indeterminate music programming. In the same folder is a link to a fun rendering of the piece on YouTube and the score for the piece, as well as one representative MIDI performance.

- music.py -
  The main set of classes and methods for working with musical objects. Most of it is developed, except I have not done much with the Melody class. Classes include Pitch, Interval, OrderedPitchSet (this is more of a "helper" for melodies) and UnorderedPitchSet (same but for chords and scales), Melody, Tracks, and Note and MidiEvent and MetaEvent as helper classes for Tracks, so that they can be easily turned into MIDI. Tracks are basically lists of Notes that each have a pitch, time, duration, and velocity (volume), and articulation (though I have not used the articulation much).
  Almost all classes have a string representation. I tried to make as many things flexible as I could, like being able to pass in a Pitch object or an integer signifying a MIDI pitch.

- midiwrite.py -
  The write function takes a Track object from music.py and outputs a MIDI file representation of it. It was slightly easier to create because I don't have to worry about external programs adding on their own events and commands. It lacks some generality, but for particles/particles.py it works. Many of the parameters in MIDI files are not changeable at the moment, like the time signature is always 60 bpm.

- midiread.py -
  The toTrack function takes a MIDI file name as input and returns a Track object from music.py. It runs through the midi file and processes each "event", and then adds it on. Turn the testing variable at the top to True to see all of the action in the testing/demo.py. One of the difficult challenges in this and the midiwrite.py was to handle MIDI's variable length values; it often uses sets of 1 to 4 bytes where the most significant bit signals to keep going to the next byte (because the number is too big) or to stop.

- mappings.py -
  A lot of useful dictionaries, two-way dictionaries (which are just dictionaries), and functions that the other programs use. I didn't want them to get all mixed up. :-)

- idk -
  Don't worry about it.

- README.txt -
  A text file that goes "PythonMusic Library....."