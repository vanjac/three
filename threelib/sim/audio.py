__author__ = "jacobvanthoog"

from collections import namedtuple
import struct

# rate is in Hz
# channels is the number of channels
# width is in bytes
# unsigned is a boolean
SampleProperties = namedtuple("SampleProperties",
    ["rate", "channels", "width", "unsigned"])

DEFAULT_PROPERTIES = \
    SampleProperties(rate=44100, width=2, unsigned=False, channels=1)

# TODO: width of 4 doesn't work

def propertiesForWave(w):
    sampleWidth = w.getsampwidth()
    return SampleProperties(rate=w.getframerate(), width=sampleWidth,
                            unsigned=sampleWidth==1, channels=w.getnchannels())

def _structFormatForSampleProperties(props):
    c = "xbhxixxxq"[props.width]
    if props.unsigned:
        c = c.upper()
    return '<' + c

def _frameSize(props):
    return props.width * props.channels

def _secondSize(props):
    return _frameSize(props) * props.rate

class AudioStream:

    def read(self, frames):
        """
        Get audio data for the specified number of seconds.
        """

    def getSampleProperties(self):
        """
        Return SampleProperties
        """
        return SampleProperties(rate=0, channels=0, width=0, unsigned=False)


    def finished(self):
        """
        Return if the audio stream is finished.
        """
        return False


class Sound(AudioStream):
    """
    An AudioStream that supports skipping, starting/stopping, looping, etc.
    """

    def __init__(self):
        self.completeAction = None
        self.playing = False
        self.isFinished = False

    # utilities for subclasses

    def _complete(self):
        self.playing = False
        if self.completeAction is not None:
            self.completeAction()

    # implement these:

    def _time(self):
        return 0

    def length(self):
        """
        Get the length in seconds of the sound.
        """
        pass

    def _play(self, time):
        pass

    def _stop(self):
        pass

    def _read(self, frames):
        return bytes()

    # don't override these

    def kill(self):
        """
        Mark this Sound as finished.
        """
        self.isFinished = True

    def play(self, time=0):
        """
        Start the Sound at a specific time in seconds, or the beginning if no
        time is specified. If the sound is already playing, jump to the time.
        """
        self.playing = True
        self._play(time)

    def stop(self):
        """
        Stop playing the Sound.
        """
        self.playing = False
        self._stop()

    def isPlaying(self):
        """
        Return True if this Sound is playing.
        """
        return self.playing

    def time(self):
        """
        Get the current time in seconds being played.
        """
        if self.playing:
            return self._time()
        return None

    def setCompleteAction(self, function=None):
        """
        Set a function (that accepts no arguments) to be called when the sound
        is complete. None for no action.

        You could use this to make the sound loop:
        ``sound.setCompleteAction(sound.play)``

        or to make it mark itself as finished when it completes:
        ``sound.setCompleteAction(sound.kill)``
        """
        self.completeAction = function

    def finished(self):
        return self.isFinished

    def read(self, frames):
        if not self.playing:
            return bytes([0 for i in range(0,
                frames * _frameSize(self.getSampleProperties()))])
        return self._read(frames)


class AudioDataStream(Sound):

    def __init__(self, data, properties=None):
        super().__init__()
        if properties is None:
            properties = DEFAULT_PROPERTIES
        self.data = data
        self.properties = properties
        self.i = 0

    def _play(self, time):
        self.i = _secondSize(self.properties) * time

    def _time(self):
        return float(self.i) / _secondSize(self.properties)

    def length(self):
        return float(len(self.data) / _secondSize(self.properties))

    def _read(self, frames):
        frameSize = _frameSize(self.properties)
        if self.i >= len(self.data):
            self._complete()
            return bytes([0 for i in range(0, frames * frameSize)])
        dataSize = frames * frameSize
        data = self.data[self.i : self.i + dataSize]
        self.i += len(data)
        if len(data) < dataSize:
            data += bytes([0 for i in range(0, dataSize - len(data))])
        return data

    def getSampleProperties(self):
        return self.properties


class AudioStreamSequence(AudioStream):

    def __init__(self, streams, properties=None):
        if properties is None:
            properties = DEFAULT_PROPERTIES
        self.streams = streams
        self.streamI = 0
        self.properties = properties

    def read(self, frames):
        framesRemaining = frames
        frameSize = _frameSize(self.properties)
        data = bytes()

        while framesRemaining > 0:
            if self.streamI >= len(self.streams):
                break
            stream = self.streams[self.streamI]
            if stream.finished():
                self.streamI += 1
                continue
            data += stream.read(framesRemaining)
            framesRemaining = frames - len(data) / frameSize
            if stream.finished():
                self.streamI += 1
            else:
                if framesRemaining > 0:
                    print("Warning: Incomplete stream!")
                break
        return data

    def getSampleProperties(self):
        return self.properties

    def finished(self):
        return self.streamI >= len(self.streams)


class BitshiftVariationsStream(AudioStream):

    # Credit to Rob Miles: https://youtu.be/MqZgoNRERY8

    def __init__(self):
        self.i = 0

    def getSampleProperties(self):
        return SampleProperties(rate=8000, channels=1, width=1, unsigned=True)

    # i: loop iteration
    # x: controls timbre/volume/octave of sound? certain values will disable sound
    # n: note selection from a set of 8 notes (switches between 2 chords over time)
    # o: octave: higher numbers = lower octave
    def _g(self, i, x, n, octave):
        #             more likely                      less likely
        chordString = "BY}6YB6%" if 3 & (i >> 16) else "Qj}6jQ6%"
        note = ord(chordString[n % 8]) + 51
        return (3 & x & (i * note >> octave)) << 4

    def read(self, frames):
        data = bytes()
        for j in range(0, frames):
            n = self.i >> 14
            s = self.i >> 17
            value = (self._g(self.i, 1, n, 12)
                   + self._g(self.i, s, n ^ self.i >> 13, 10)
                   + self._g(self.i, s // 3, n + ((self.i >> 11) % 3), 10)
                   + self._g(self.i, s // 5, 8 + n - ((self.i >> 10) % 3), 9)
                     )
            data += bytes([value])
            self.i += 1
        return data

    def finished(self):
        return False


class NoteStream(AudioStream):

    def __init__(self, frequency, length, properties=None):
        if properties is None:
            properties = DEFAULT_PROPERTIES
        self.frequency = frequency
        self.length = length
        self.properties = properties
        self.i = 0

    def read(self, frames):
        if self.finished():
            return bytes([0 for i in range(0,
                                           frames*_frameSize(self.properties))])
        data = bytes()
        props = self.getSampleProperties()
        structFormat = _structFormatForSampleProperties(props)
        maxValue = 2 ** (props.width * 8)
        for j in range(0, frames):
            value = int(float(self.i) * self.frequency * maxValue / props.rate)
            value %= maxValue
            if not props.unsigned:
                value -= maxValue // 2
            newData = bytes(struct.pack(structFormat, value))
            for k in range(0, props.channels):
                data += newData
            self.i += 1
        return data

    def getSampleProperties(self):
        return self.properties

    def finished(self):
        return self.i > self.length * self.getSampleProperties().rate


class AmplitudeModifier(AudioStream):

    # TODO: doesn't work with width=2, unsigned=True

    def __init__(self, stream, amplitude=1.0):
        self.stream = stream
        self.amplitude = amplitude

    def setAmplitude(self, amplitude):
        self.amplitude = amplitude

    def read(self, frames):
        data = self.stream.read(frames)

        props = self.getSampleProperties()
        structFormat = _structFormatForSampleProperties(props)
        maxValue = 2 ** (props.width * 8) // 2 # assuming signed values
        newData = bytes()

        for i in range(0, len(data) // props.width):
            dataValue = data[i * props.width : (i+1) * props.width]
            values = struct.unpack(structFormat, dataValue)
            assert len(values) == 1
            value = values[0]
            if props.unsigned:
                value -= maxValue
            value *= self.amplitude
            value = int(value)
            if value >= maxValue:
                value = maxValue - 1
            if value <= -maxValue:
                value = -maxValue + 1
            if props.unsigned:
                value += maxValue
            dataValue = struct.pack(structFormat, value)
            newData += dataValue

        return newData

    def getSampleProperties(self):
        return self.stream.getSampleProperties()

    def finished(self):
        return self.stream.finished()


class AudioMixer(AudioStream):

    def __init__(self, keepOpen=False, properties=None):
        if properties is None:
            properties = DEFAULT_PROPERTIES
        self.streams = [ ]
        self.properties = properties
        self.keepOpen = keepOpen

    def addStream(self, stream):
        self.streams.append(stream)

    def removeStream(self, stream):
        self.streams.remove(stream)

    def read(self, frames):
        finishedStreams = [ ]
        for stream in self.streams:
            if stream.finished():
                finishedStreams.append(stream)
        for stream in finishedStreams:
            self.streams.remove(stream)

        structFormat = _structFormatForSampleProperties(self.properties)
        maxValue = 2 ** (self.properties.width * 8) // 2  # assuming signed
        mixedData = bytes()

        streamData = [stream.read(frames) for stream in self.streams]

        for i in range(0, frames * self.properties.channels):
            mixedValue = maxValue if self.properties.unsigned else 0
            for data in streamData:
                try:
                    dataValue = data[i * self.properties.width
                                     : (i+1) * self.properties.width]
                except IndexError:
                    continue
                value = struct.unpack(structFormat, dataValue)[0]
                if self.properties.unsigned:
                    value -= maxValue
                mixedValue += value
            if self.properties.unsigned:
                if mixedValue >= maxValue * 2:
                    mixedValue = maxValue * 2 - 1
                if mixedValue <= 0:
                    mixedValue = 0
            else:
                if mixedValue >= maxValue:
                    mixedValue = maxValue - 1
                if mixedValue <= -maxValue:
                    mixedValue = -maxValue + 1
            mixedDataValue = struct.pack(structFormat, mixedValue)
            mixedData += mixedDataValue

        return mixedData

    def getSampleProperties(self):
        return self.properties

    def finished(self):
        for stream in self.streams:
            if not stream.finished():
                return False
        return not self.keepOpen
