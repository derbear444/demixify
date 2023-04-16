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

warnings.filterwarnings("ignore")

nussl.utils.seed(0)

curr_dir = os.getcwd()
api_dir = os.path.join(curr_dir, 'api')
checkpoint_dir = os.path.join(api_dir, 'checkpoints')
combos_dir = os.path.join(api_dir, 'combos')

def visualize_and_embed_notebook(sources):
    plt.figure(figsize=(10, 6))
    plt.subplot(211)
    nussl.utils.visualize_sources_as_masks(sources,
        y_axis='mel', db_cutoff=-40, alpha_amount=2.0)
    plt.subplot(212)
    nussl.utils.visualize_sources_as_waveform(
        sources, show_legend=False)
    plt.show()
    nussl.play_utils.multitrack(sources)

def visualize_and_embed(sources):
    plt.figure(figsize=(10, 6))
    plt.subplot(211)
    nussl.utils.visualize_sources_as_masks(sources,
        y_axis='mel', db_cutoff=-40, alpha_amount=2.0)
    plt.subplot(212)
    nussl.utils.visualize_sources_as_waveform(
        sources, show_legend=False)
    plt.show()
    return nussl.play_utils.multitrack(sources)

def visualize(song_name):

    if song_name not in defaults.SONG_LIST:
        return "Request song not in database."
    
    start_time = time.time()

    combo_name = "%s-combined.npy" %(song_name)
    combo_path = os.path.join(combos_dir, combo_name)

    final_ests = []
    with open(combo_path, 'rb') as f:
        final_ests = np.load(f, allow_pickle=True)

    fin_estimates = {f'Source {i}': e for i, e in enumerate(final_ests)}
    end_time = time.time()
    time_taken = end_time - start_time
    time_string = f'Time taken: {time_taken:.4f} seconds'
    return visualize_and_embed(fin_estimates)