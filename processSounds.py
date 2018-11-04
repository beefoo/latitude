# -*- coding: utf-8 -*-

import argparse
import array
import glob
import json
import os
import numpy as np
from pprint import pprint
from pydub import AudioSegment
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILES", default="data/downloads/orchestra/*", help="Input file pattern")
parser.add_argument('-stetch', dest="STRETCH_TO", default=5000, type=int, help="Stretch each clip to this duration in ms")
parser.add_argument('-fin', dest="FADE_IN", default=100, type=int, help="Fade in ms")
parser.add_argument('-fout', dest="FADE_OUT", default=100, type=int, help="Fade out ms")
parser.add_argument('-audio', dest="AUDIO_FILE", default="ui/audio/orchestra.mp3", help="Output audio file")
parser.add_argument('-sprite', dest="SPRITE_FILE", default="ui/audio/orchestra.json", help="Output sprite file")
args = parser.parse_args()

INPUT_FILES = args.INPUT_FILES
STRETCH_TO = args.STRETCH_TO
FADE_IN = args.FADE_IN
FADE_OUT = args.FADE_OUT
AUDIO_FILE = args.AUDIO_FILE
SPRITE_FILE = args.SPRITE_FILE

SAMPLE_WIDTH = 2
FRAME_RATE = 44100
CHANNELS = 2
POWER_LEVEL = -24

def setPowerLevel(sound, targetLevel):
    difference = targetLevel - sound.dBFS
    return sound.apply_gain(difference)

# Adapted from: https://github.com/paulnasca/paulstretch_python/blob/master/paulstretch_newmethod.py
def paulStretch(samplerate, smp, stretch, windowsize_seconds=0.25, onset_level=10.0):
    nchannels=smp.shape[0]

    def optimize_windowsize(n):
        orig_n=n
        while True:
            n=orig_n
            while (n%2)==0:
                n/=2
            while (n%3)==0:
                n/=3
            while (n%5)==0:
                n/=5

            if n<2:
                break
            orig_n+=1
        return orig_n

    #make sure that windowsize is even and larger than 16
    windowsize=int(windowsize_seconds*samplerate)
    if windowsize<16:
        windowsize=16
    windowsize=optimize_windowsize(windowsize)
    windowsize=int(windowsize/2)*2
    half_windowsize=int(windowsize/2)

    #correct the end of the smp
    nsamples=smp.shape[1]
    end_size=int(samplerate*0.05)
    if end_size<16:
        end_size=16

    smp[:,nsamples-end_size:nsamples]*=np.linspace(1,0,end_size)


    #compute the displacement inside the input file
    start_pos=0.0
    displace_pos=windowsize*0.5

    #create Hann window
    window=0.5-np.cos(np.arange(windowsize,dtype='float')*2.0*np.pi/(windowsize-1))*0.5

    old_windowed_buf=np.zeros((2,windowsize))
    hinv_sqrt2=(1+np.sqrt(0.5))*0.5
    hinv_buf=2.0*(hinv_sqrt2-(1.0-hinv_sqrt2)*np.cos(np.arange(half_windowsize,dtype='float')*2.0*np.pi/half_windowsize))/hinv_sqrt2

    freqs=np.zeros((2,half_windowsize+1))
    old_freqs=freqs

    num_bins_scaled_freq=32
    freqs_scaled=np.zeros(num_bins_scaled_freq)
    old_freqs_scaled=freqs_scaled

    displace_tick=0.0
    displace_tick_increase=1.0/stretch
    if displace_tick_increase>1.0:
        displace_tick_increase=1.0
    extra_onset_time_credit=0.0
    get_next_buf=True

    sdata = np.array([])
    while True:
        if get_next_buf:
            old_freqs=freqs
            old_freqs_scaled=freqs_scaled

            #get the windowed buffer
            istart_pos=int(np.floor(start_pos))
            buf=smp[:,istart_pos:istart_pos+windowsize]
            if buf.shape[1]<windowsize:
                buf=np.append(buf,np.zeros((2,windowsize-buf.shape[1])),1)
            buf=buf*window

            #get the amplitudes of the frequency components and discard the phases
            freqs=abs(np.fft.rfft(buf))

            #scale down the spectrum to detect onsets
            freqs_len=freqs.shape[1]
            if num_bins_scaled_freq<freqs_len:
                freqs_len_div=freqs_len//num_bins_scaled_freq
                new_freqs_len=freqs_len_div*num_bins_scaled_freq
                freqs_scaled=np.mean(np.mean(freqs,0)[:new_freqs_len].reshape([num_bins_scaled_freq,freqs_len_div]),1)
            else:
                freqs_scaled=np.zeros(num_bins_scaled_freq)


            #process onsets
            m=2.0*np.mean(freqs_scaled-old_freqs_scaled)/(np.mean(abs(old_freqs_scaled))+1e-3)
            if m<0.0:
                m=0.0
            if m>1.0:
                m=1.0
            # if plot_onsets:
            #     onsets.append(m)
            if m>onset_level:
                displace_tick=1.0
                extra_onset_time_credit+=1.0

        cfreqs=(freqs*displace_tick)+(old_freqs*(1.0-displace_tick))

        #randomize the phases by multiplication with a random complex number with modulus=1
        ph=np.random.uniform(0,2*np.pi,(nchannels,cfreqs.shape[1]))*1j
        cfreqs=cfreqs*np.exp(ph)

        #do the inverse FFT
        buf=np.fft.irfft(cfreqs)

        #window again the output buffer
        buf*=window

        #overlap-add the output
        output=buf[:,0:half_windowsize]+old_windowed_buf[:,half_windowsize:windowsize]
        old_windowed_buf=buf

        #remove the resulted amplitude modulation
        output*=hinv_buf

        #clamp the values to -1..1
        output[output>1.0]=1.0
        output[output<-1.0]=-1.0

        #write the output to wav file
        # outfile.writeframes(int16(output.ravel(1)*32767.0).tostring())
        sdata = np.append(sdata, output.ravel(1), axis=0)

        if get_next_buf:
            start_pos+=displace_pos

        get_next_buf=False

        if start_pos>=nsamples:
            # print ("100 %")
            break
        # sys.stdout.write("%d %% \r" % int(100.0*start_pos/nsamples))
        # sys.stdout.flush()

        if extra_onset_time_credit<=0.0:
            displace_tick+=displace_tick_increase
        else:
            credit_get=0.5*displace_tick_increase #this must be less than displace_tick_increase
            extra_onset_time_credit-=credit_get
            if extra_onset_time_credit<0:
                extra_onset_time_credit=0
            displace_tick+=displace_tick_increase-credit_get

        if displace_tick>=1.0:
            displace_tick=displace_tick % 1.0
            get_next_buf=True

    sdata = sdata * 32767.0
    sdata = sdata.astype(np.int16)
    return sdata

def stretchSound(sound, amount=2.0):
    channels = sound.channels
    frame_rate = sound.frame_rate
    samples = np.array(sound.get_array_of_samples())
    samples = samples.astype(np.int16)
    samples = samples * (1.0/32768.0)
    if channels > 1:
        samples = samples.reshape(channels, len(samples)/channels, order='F')
    newData = paulStretch(frame_rate, samples, amount)
    newData = array.array(sound.array_type, newData)
    newSound = sound._spawn(newData)
    return newSound

files = glob.glob(INPUT_FILES)
fileCount = len(files)
print("Found %s files" % fileCount)

duration = fileCount * STRETCH_TO
baseAudio = AudioSegment.silent(duration=duration, frame_rate=FRAME_RATE)
baseAudio = baseAudio.set_channels(CHANNELS)
baseAudio = baseAudio.set_sample_width(SAMPLE_WIDTH)
sprites = {}

print("Processing files...")
for i, fn in enumerate(files):
    basename = os.path.basename(fn).split(".")[0]

    fformat = fn.split(".")[-1].lower()
    audio = AudioSegment.from_file(fn, format=fformat)

    # convert to stereo
    if audio.channels != CHANNELS:
        print("Notice: changed %s to %s channels" % (fn, CHANNELS))
        audio = audio.set_channels(CHANNELS)
    # convert sample width
    if audio.sample_width != SAMPLE_WIDTH:
        print("Warning: sample width changed to %s from %s in %s" % (SAMPLE_WIDTH, audio.sample_width, fn))
        audio = audio.set_sample_width(SAMPLE_WIDTH)
    # convert sample rate
    if audio.frame_rate != FRAME_RATE:
        print("Warning: frame rate changed to %s from %s in %s" % (FRAME_RATE, audio.frame_rate, fn))
        audio = audio.set_frame_rate(FRAME_RATE)

    audioDur = len(audio)
    # clip if too long
    if audioDur > STRETCH_TO:
        audio = audio[:STRETCH_TO]

    # stretch if too short
    else:
        amount = 1.0 * STRETCH_TO / audioDur
        audio = stretchSound(audio, amount)

    # attempt to set power level evenly
    audio = setPowerLevel(audio, POWER_LEVEL)

    audio = audio.fade_in(FADE_IN).fade_out(FADE_OUT)
    position = i * STRETCH_TO
    baseAudio = baseAudio.overlay(audio, position=position)
    sprites[basename] = [position, STRETCH_TO]
    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/fileCount*100,1))
    sys.stdout.flush()

print("Writing to file...")
fformat = AUDIO_FILE.split(".")[-1]
f = baseAudio.export(AUDIO_FILE, format=fformat)
print("Wrote to %s" % AUDIO_FILE)

with open(SPRITE_FILE, 'w') as f:
    json.dump(sprites, f, sort_keys = True, indent = 2)
    print("Wrote to %s" % SPRITE_FILE)
