# Arjoonn Sharma
import math  # for the math we need
import wave  # fow writing .WAV files
import struct  # bit level manupulation
from PIL import Image  # reading the image
import itertools as itt  # nice tools


def tone(freq=440., framerate=44100, skip_frame=0):
    "Generate a pure tone of max amp = 1"
    for i in itt.count(skip_frame):
        sine = math.sin(2.0 * math.pi * freq * (float(i) / float(framerate)))
        yield sine

def get_key_freq(n):
    """
    Return's the freq of n'th piano key in Hz
    taken from:
        https://en.wikipedia.org/wiki/Piano_key_frequencies
    """
    power = (n - 49.) / 12.
    return ((2.)**power) * 440.

def get_image_data_sequence(imagename):
    "Get the image data as a list of lists containing pixel values"
    image = Image.open(imagename).convert(mode='L')
    width = image.width
    count, temp, data = 0, [], []
    for value in image.getdata():
        if count >= width:
            count = 0
            data.append(temp)
            temp = []
        temp.append(value / 255.)
        count += 1
    return data

def play_piano(image):
    "Create a generator which output's the values of the sound amplitude"
    n_keys = len(image[0])
    # get piano key tone frequencies
    tone_list = [tone(get_key_freq(i + 1)) for i in range(n_keys)]
    # Amp modulate as per image pixel values
    image_height = float(len(image))
    for index, tone_values in enumerate(zip(*tone_list)):
        index = int(index % image_height)
        complete_value = sum(t * v for t, v in zip(tone_values, image[index])) / image_height
        yield complete_value

def write_wavefile(f, samples, nframes=None, nchannels=2, sampwidth=2, framerate=44100, bufsize=2048):
    "Write samples to a wavefile."
    if nframes is None:
        nframes = 0
    max_amplitude = float(int((2 ** (sampwidth * 8)) / 2) - 1)
    with wave.open(f, 'wb') as w:
        w.setparams((nchannels, sampwidth, framerate, nframes, 'NONE', 'not compressed'))

        frames = b''.join(struct.pack('h', int(max_amplitude * sample)) for sample in samples)
        w.writeframesraw(frames)
 

# --------------------------------------------------extras
if __name__ == '__main__':
    import sys
    image = get_image_data_sequence(sys.argv[1])
    piano = itt.islice(play_piano(image), 44100 * 5)  # 5 seconds

    name = sys.argv[1].replace('.', '_') + '.wav'
    write_wavefile(name, piano, bufsize=2**15, nchannels=1)
