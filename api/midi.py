import nussl
import time
import warnings
import os, subprocess
import wave
from scipy.io.wavfile import write
import zipfile

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = 'max_split_size_mb:32000'

warnings.filterwarnings("ignore")

nussl.utils.seed(0)

curr_dir = os.getcwd()
api_dir = os.path.join(curr_dir, 'api')
checkpoint_dir = os.path.join(api_dir, 'checkpoints')
combos_dir = os.path.join(api_dir, 'combos')
wav_dir = os.path.join(api_dir, 'wav_midi')
midi_dir = os.path.join(api_dir, 'midi')

# deletes unnecessary files
def delete_temps(filename):
    # Deletes unnecessary files in wav_dir
    for fname in os.listdir(wav_dir):
        if fname.startswith(filename):
            os.remove(os.path.join(wav_dir, fname))
    # Deletes unnecessary files in midi_dir
    for fname in os.listdir(midi_dir):
        if fname.startswith(filename):
            os.remove(os.path.join(midi_dir, fname))

# get zip
def get_zip(zip_name):
    for fname in os.listdir(midi_dir):
        if fname == zip_name:
            with open(os.path.join(midi_dir, fname), 'rb') as midi:
                return midi.read()

# zips needed files into archive
def zip_midis(filename, zip_name):
    files_to_zip = [f for f in os.listdir(midi_dir) if f.startswith(filename)]
    zip_path = os.path.join(midi_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files_to_zip:
            file_path = os.path.join(midi_dir, file)
            zip_file.write(file_path, arcname=file)
    
    print(f'Successfully created {zip_name} containing {len(files_to_zip)} files.')
    return zip_path

# saves file to wav location to then be turned into midi
def savefile(blob, filename, sr):
    start_time = time.time()

    path = os.path.join(wav_dir, filename)
    with wave.open(path, 'wb') as wav:
        wav.setnchannels(2)  # assume stereo audio
        wav.setsampwidth(2)  # assume 16-bit audio
        wav.setframerate(float(sr)) # sampling rate
        wav.writeframes(blob)
    
    midify(filename)

    end_time = time.time()
    time_taken = end_time - start_time
    time_string = f'Time taken: {time_taken:.4f} seconds'
    print(time_string)
    return time_string

# runs Spotify's basic pitch on files in wav_dir
def midify(filename):
    wavs = []
    for fname in os.listdir(wav_dir):
        if fname.startswith(filename):
            wavs.append(os.path.join(wav_dir, fname))

    cmd = wavs
    cmd.insert(0, os.path.relpath(midi_dir))
    cmd.insert(0, 'basic-pitch')
    call = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    print(str(call.stdout))

