import sys
import librosa

from sound_to_midi.monophonic import wave_to_midi

def convert(file_in, file_out):
    try:
        print("Starting...")
        file_in = file_in
        file_out = file_out
        y, sr = librosa.load(file_in, sr=44100)
        print("Audio file loaded!")
        midi = wave_to_midi(y, srate=sr)
        print("Conversion finished!")
        with open (file_out, 'wb') as f:
            midi.writeFile(f)
        print("Done. Exiting!")
    except Exception as e:
        print(e)
        sys.exit(1)