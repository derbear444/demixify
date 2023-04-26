import nussl
import matplotlib.pyplot as plt
import time
import numpy as np
import warnings
import torch
import os
import api.defaults as defaults
import librosa
import re

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = 'max_split_size_mb:32000'

warnings.filterwarnings("ignore")

nussl.utils.seed(0)

curr_dir = os.getcwd()
api_dir = os.path.join(curr_dir, 'api')
checkpoint_dir = os.path.join(api_dir, 'checkpoints')
combos_dir = os.path.join(api_dir, 'combos')
data_dir = os.path.join(api_dir, 'data')

Fs = defaults.SAMPLE_RATE
NUM_SOURCES = defaults.NUM_SOURCES
NUM_ITERATIONS = defaults.NUM_ITERATIONS
checkpoint = True

def run(self):
        P, Q = self.initialize_parameters()
        for i in range(self.num_iterations):
            P, Q = self._update(P, Q)

        KQ = self._get_kq(Q)
        KQ = KQ.reshape(KQ.shape[0], -1, 1, KQ.shape[-1])
        sigma_j = KQ * P[:, None, ...]
        sigma_j = sigma_j / (self.eps + sigma_j.sum(dim=-1)[..., None])
        sigma_j = self._convert_to_numpy(sigma_j)

        self.projection_set = self.projection_set.reshape(
            self.projection_set.shape[0],
            self.projection_set.shape[1] * self.projection_set.shape[2],
            self.projection_set.shape[-1]
        )

        self.inverse_projection_set = np.linalg.pinv(self.projection_set)

        cf_j = (
                (self.projection_set @
                 self.stft.transpose(0, 2, 1))[..., None]
                * sigma_j
        )
        shape = cf_j.shape

        reconstructions = (
                self.inverse_projection_set @
                cf_j.reshape(
                    cf_j.shape[0],
                    cf_j.shape[1],
                    -1
                )
        )
        reconstructions = reconstructions.reshape(
            shape[0], self.stft.shape[-1], -1, shape[-1]
        )

        self.reconstructions = np.swapaxes(reconstructions, 1, 2)

        return reconstructions

def _update(self, P, Q):
        KQ = self._get_kq(Q)
        sigma = self._update_sigma(P, Q, KQ)
        P = self._update_P(P, sigma, KQ)
        P[P < 1e-300] = 1e-300
        sigma = self._update_sigma(P, Q, KQ)
        Q = self._update_Q(P, sigma, Q)
        Q[Q < 1e-300] = 1e-300
        return P, Q

nussl.separation.spatial.projet.Projet.run = run
nussl.separation.spatial.projet.Projet._update = _update

# clears all the unneeded checkpoints for the given file
def cleanup(filename, excluded_checkpoint=""):
     for fname in os.listdir(checkpoint_dir):
        if fname.startswith(filename) and fname != excluded_checkpoint:
            os.remove(os.path.join(checkpoint_dir, fname))

# takes a filename and splits the song up in sources
def demix(filename):
    start_time = time.time()

    fn_wav_X = os.path.join(data_dir, filename)

    final_ests = []
    if checkpoint:
        checkpoint_name = '%s-checkpoint-13.npy' %(filename)
        with open(os.path.join(checkpoint_dir, checkpoint_name), 'rb') as f:
            final_ests = np.load(f, allow_pickle=True)
    # Loads song first time to grab sample rate
    audio_data_array, Fs = librosa.load(fn_wav_X, mono=False, sr=None)
    # Loads again based on half the sample rate
    audio_data_array, Fs = librosa.load(fn_wav_X, mono=False, sr=Fs/2)

    # Split audio into 10-second segments
    duration = defaults.SPLIT_DURATION * Fs # duration of each segment in seconds
    length = audio_data_array.shape[1]
    print(f'Number of splits necessary: {np.floor(length/duration)}')
    segments = final_ests.tolist() if checkpoint else []
    checkpoint_start = len(segments)-1 if checkpoint else 0
    last_checkpoint_name = ""

    for i, start in enumerate(range(0, length, duration)):
        if i >= checkpoint_start:
            end = min(start + duration, length)
            segment = audio_data_array[:, start:end]
            
            curr_mix = nussl.AudioSignal(audio_data_array=segment, sample_rate=Fs)
            
            DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
            separator = nussl.separation.spatial.Projet(
                curr_mix, num_sources=NUM_SOURCES, device=DEVICE, num_iterations=NUM_ITERATIONS)

            estimates = separator()

            segments.append(estimates)

            last_checkpoint_name = "%s-checkpoint-%d.npy" %(filename, i)
            with open(os.path.join(checkpoint_dir, last_checkpoint_name), 'wb') as f:
                np.save(f, np.array(segments), allow_pickle=True)

    end_time = time.time()
    time_taken = end_time - start_time
    time_string = f'Time taken: {time_taken:.4f} seconds'
    return time_string

# takes a filename and splits the song up in sources
def demix_with_checkpoint(filename):
    start_time = time.time()

    fn_wav_X = os.path.join(data_dir, filename)

    final_ests = []
    checkpoint_name = ''
    if checkpoint:
        checkpoint_nums = []
        # Loops through all checkpoints that match the filename
        for fname in os.listdir(checkpoint_dir):
            if fname.startswith(filename):
                m = re.search(r'(.*)-checkpoint-(\d+).npy', fname)
                if m:
                    checkpoint_nums.append(int(m.group(2)))
        if len(checkpoint_nums) != 0:
            # Gets the latest checkpoint recorded and loads it
            checkpoint_name = '%s-checkpoint-%d.npy' %(filename, max(checkpoint_nums))
            with open(os.path.join(checkpoint_dir, checkpoint_name), 'rb') as f:
                final_ests = np.load(f, allow_pickle=True)
            print(f'Resuming with checkpoint: {checkpoint_name}')

    audio_data_array, Fs = librosa.load(fn_wav_X, mono=False, sr=None)

    # Split audio into 10-second segments
    duration = defaults.SPLIT_DURATION * Fs # duration of each segment in seconds
    length = audio_data_array.shape[1]
    max_splits = np.floor(length/duration)
    print(f'Number of splits necessary: {max_splits}')
    segments = final_ests.tolist() if checkpoint_name else []
    checkpoint_start = len(segments)-1 if checkpoint_name else 0
    last_checkpoint_name = ""

    for i, start in enumerate(range(0, length, duration)):
        if i >= checkpoint_start:
            end = min(start + duration, length)
            segment = audio_data_array[:, start:end]
            
            try:
                curr_mix = nussl.AudioSignal(audio_data_array=segment, sample_rate=Fs)
                
                DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
                separator = nussl.separation.spatial.Projet(
                    curr_mix, num_sources=NUM_SOURCES, device=DEVICE, num_iterations=NUM_ITERATIONS)

                estimates = separator()

                segments.append(estimates)

                last_checkpoint_name = "%s-checkpoint-%d.npy" %(filename, i)
                with open(os.path.join(checkpoint_dir, last_checkpoint_name), 'wb') as f:
                    np.save(f, np.array(segments), allow_pickle=True)

                print("Progress: Split %d/%d" %(i, max_splits))
            except nussl.core.audio_signal.AudioSignalException:
                print("Uneven split on last segment detected.")
                print("Using last good checkpoint instead.")
                last_checkpoint_name = last_checkpoint_name if last_checkpoint_name else checkpoint_name
                print(f'Checkpoint: {last_checkpoint_name}')

    end_time = time.time()
    time_taken = end_time - start_time
    time_string = f'Time taken: {time_taken:.4f} seconds'
    return last_checkpoint_name