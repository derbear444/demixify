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
import io
import html

warnings.filterwarnings("ignore")

nussl.utils.seed(0)

curr_dir = os.getcwd()
api_dir = os.path.join(curr_dir, 'api')
checkpoint_dir = os.path.join(api_dir, 'checkpoints')
combos_dir = os.path.join(api_dir, 'combos')

def multiembed(audio_signals, names=None, ext='.mp3'):
    """
    Takes a bunch of audio sources, converts them to mp3 to make them smaller, and
    creates a multitrack audio player in the notebook that lets you
    toggle between the sources and the mixture. Heavily adapted
    from https://github.com/binarymind/multitrackHTMLPlayer,
    designed by Bastien Liutkus.

    Args:
        audio_signals (list): List of AudioSignal objects that add up to the mixture.
        names (list): List of names to give to each object (e.g. foreground, background).
        ext (str): What extension to use when embedding. '.mp3' is more lightweight
          leading to smaller notebook sizes.
        display (bool): Whether or not to display the object immediately, or to return
          the html object for display later by the end user.
    """
    _names = None

    if isinstance(audio_signals, dict):
        _names = list(audio_signals.keys())
        audio_signals = [audio_signals[k] for k in _names]

    if names is not None:
        if len(names) != len(audio_signals):
            raise ValueError("len(names) must be equal to len(audio_signals)!")
    else:
        if _names is not None:
            names = _names
        else:
            names = [
                f"{i}:{s.path_to_input_file}"
                for i, s in enumerate(audio_signals)
            ]

    encoded_audios = []
    for name, signal in zip(names, audio_signals):
        encoded_audio = nussl.play_utils.embed_audio(signal, ext=ext, display=False).src_attr()
        encoded_audios.append({'name': name, 'audio': encoded_audio})

    return encoded_audios

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

def graph(sourcesg):
    plt.figure(figsize=(10, 6))
    plt.subplot(211)
    nussl.utils.visualize_sources_as_masks(sources,
        y_axis='mel', db_cutoff=-40, alpha_amount=2.0)
    plt.subplot(212)
    nussl.utils.visualize_sources_as_waveform(
        sources, show_legend=False)
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image

def audio(sources):
    ret = nussl.play_utils.multiembed(sources, display=False)
    return ret.data

def embeded_audio(sources):
    ret = multiembed(sources)
    return ret

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
    return graph(fin_estimates)

def generate_audio(song_name):

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
    return audio(fin_estimates)

def generate_embeded_audio(song_name):

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
    return embeded_audio(fin_estimates)