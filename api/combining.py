import nussl
import matplotlib.pyplot as plt
import time
import numpy as np
import warnings
import torch
import librosa
import librosa.display
import os
import api.defaults as defaults

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = 'max_split_size_mb:32000'

warnings.filterwarnings("ignore")

nussl.utils.seed(0)

curr_dir = os.getcwd()
api_dir = os.path.join(curr_dir, 'api')
checkpoint_dir = os.path.join(api_dir, 'checkpoints')
combos_dir = os.path.join(api_dir, 'combos')

def combine(song_name, checkpoint_name):

    if song_name not in defaults.SONG_LIST:
        return "Request song not in database."
    
    start_time = time.time()
    
    checkpoint_path = os.path.join(checkpoint_dir, checkpoint_name)

    final_ests = []
    with open(checkpoint_path, 'rb') as f:
        final_ests = np.load(f, allow_pickle=True)

    Fs = defaults.SAMPLE_RATE
    duration = defaults.SPLIT_DURATION * Fs # duration of each segment in seconds

    # Combines 
    for i, list in enumerate(final_ests):
        if i > 0:
            for j in range(0, 6):
                if j < len(list): # Combine the sources across the different lists with the first signal audio objects
                    final_ests[0][j].concat(list[j])
                elif j < len(final_ests[0]): # If there is no corresponding source, pad with zeros
                    final_ests[0][j].zero_pad(0, duration)

    combo_name = "%s-combined.npy" %(song_name)
    combo_path = os.path.join(combos_dir, combo_name)
    # Save new combined signal audio objects to be loaded by notebook
    with open(combo_path ,'wb') as f:
          np.save(f, np.array(final_ests[0]), allow_pickle=True)

    end_time = time.time()
    time_taken = end_time - start_time
    time_string = f'Time taken: {time_taken:.4f} seconds'
    return time_string

def combine_with_combo(song_name, checkpoint_name):

    if song_name not in defaults.SONG_LIST:
        return "Request song not in database."
    
    start_time = time.time()
    
    checkpoint_path = os.path.join(checkpoint_dir, checkpoint_name)

    final_ests = []
    with open(checkpoint_path, 'rb') as f:
        final_ests = np.load(f, allow_pickle=True)

    Fs = defaults.SAMPLE_RATE
    duration = defaults.SPLIT_DURATION * Fs # duration of each segment in seconds

    # Combines 
    for i, list in enumerate(final_ests):
        if i > 0:
            for j in range(0, 6):
                if j < len(list): # Combine the sources across the different lists with the first signal audio objects
                    final_ests[0][j].concat(list[j])
                elif j < len(final_ests[0]): # If there is no corresponding source, pad with zeros
                    final_ests[0][j].zero_pad(0, duration)

    combo_name = "%s-combined.npy" %(song_name)
    combo_path = os.path.join(combos_dir, combo_name)
    # Save new combined signal audio objects to be loaded by notebook
    with open(combo_path ,'wb') as f:
          np.save(f, np.array(final_ests[0]), allow_pickle=True)

    end_time = time.time()
    time_taken = end_time - start_time
    time_string = f'Time taken: {time_taken:.4f} seconds'
    return combo_name