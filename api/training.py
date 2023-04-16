import nussl
import matplotlib.pyplot as plt
import time
import numpy as np
import warnings
import torch
import librosa
import librosa.display
import os

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = 'max_split_size_mb:32000'

warnings.filterwarnings("ignore")
start_time = time.time()

nussl.utils.seed(0)

def visualize_and_embed(sources):
    plt.figure(figsize=(10, 6))
    plt.subplot(211)
    nussl.utils.visualize_sources_as_masks(sources,
        y_axis='mel', db_cutoff=-40, alpha_amount=2.0)
    plt.subplot(212)
    nussl.utils.visualize_sources_as_waveform(
        sources, show_legend=False)
    plt.show()
    nussl.play_utils.multitrack(sources)

def run(self):
        P, Q = self.initialize_parameters()
        for i in range(self.num_iterations):
            P, Q = self._update(P, Q)

        print(torch.cuda.memory_summary(device=None, abbreviated=False))

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

Fs = 48000

data_dir = os.path.join('C:', 'Users', 'Derek', 'Documents', 'Projects', 'data')
filename = 'so-much-for-stardust.wav'
fn_wav_X = os.path.join(data_dir, filename)

os.chdir(r"C:\Users\Derek\Documents\Projects\data")

final_ests = []
checkpoint = False
if checkpoint:
    checkpoint_name = '%s-checkpoint-57.npy' %(filename)
    with open(os.path.join(data_dir, checkpoint_name), 'rb') as f:
        final_ests = np.load(f, allow_pickle=True)

audio_data_array, Fs = librosa.load(filename, mono=False, sr=None)

# Split audio into 5-second segments
duration = 8 * Fs # duration of each segment in seconds
length = audio_data_array.shape[1]
segments = final_ests.tolist() if checkpoint else []
checkpoint_start = len(segments)-1 if checkpoint else 0

for i, start in enumerate(range(0, length, duration)):
  if i >= checkpoint_start:
    end = min(start + duration, length)
    segment = audio_data_array[:, start:end]
    
    curr_mix = nussl.AudioSignal(audio_data_array=segment, sample_rate=Fs)
    
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    separator = nussl.separation.spatial.Projet(
        curr_mix, num_sources=6, device=DEVICE, num_iterations=600)

    estimates = separator()

    segments.append(estimates)

    os.chdir(r"C:\Users\Derek\Documents\Projects\checkpoints")

    with open(os.path.join("%s-checkpoint-%d.npy" %(filename, i)), 'wb') as f:
      np.save(f, np.array(segments), allow_pickle=True)

    os.chdir(r"C:\Users\Derek\Documents\Projects\data")

os.chdir(r"C:\Users\Derek\Documents\Projects")

end_time = time.time()
time_taken = end_time - start_time
print(f'Time taken: {time_taken:.4f} seconds')