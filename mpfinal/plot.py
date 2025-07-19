import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wavfile
import os

def plot_waveform_and_spectrogram(original_file, stego_file):
    # Read audio files
    sr_orig, audio_orig = wavfile.read(original_file)
    sr_stego, audio_stego = wavfile.read(stego_file)

    # If stereo, convert to mono
    if len(audio_orig.shape) == 2:
        audio_orig = audio_orig[:, 0]
    if len(audio_stego.shape) == 2:
        audio_stego = audio_stego[:, 0]

    time_orig = np.linspace(0, len(audio_orig) / sr_orig, num=len(audio_orig))
    time_stego = np.linspace(0, len(audio_stego) / sr_stego, num=len(audio_stego))

    # Plot waveforms
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.title("Original Audio - Waveform")
    plt.plot(time_orig, audio_orig, color='blue')
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")

    plt.subplot(2, 2, 2)
    plt.title("Stego Audio - Waveform")
    plt.plot(time_stego, audio_stego, color='green')
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")

    # Plot spectrograms
    plt.subplot(2, 2, 3)
    plt.title("Original Audio - Spectrogram")
    plt.specgram(audio_orig, Fs=sr_orig, cmap='viridis')
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")

    plt.subplot(2, 2, 4)
    plt.title("Stego Audio - Spectrogram")
    plt.specgram(audio_stego, Fs=sr_stego, cmap='viridis')
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")

    plt.tight_layout()
    plt.show()

# --- Run the comparison ---
if __name__ == "__main__":
    original = input("Enter path to original WAV file: ")
    stego = input("Enter path to stego WAV file: ")
    if os.path.exists(original) and os.path.exists(stego):
        plot_waveform_and_spectrogram(original, stego)
    else:
        print("One or both files not found.")
