# import numpy as np
# import wave
# import sys
# import os

# def read_wav_file(filename):
#     with wave.open(filename, 'rb') as wf:
#         frames = wf.readframes(wf.getnframes())
#         data = np.frombuffer(frames, dtype=np.int16).astype(np.float64)  # Cast to float64
#     return data

# def calculate_snr(original, stego):
#     noise = original - stego
#     signal_power = np.mean(original ** 2)
#     noise_power = np.mean(noise ** 2)
#     snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
#     return snr

# def calculate_mse(original, stego):
#     return np.mean((original - stego) ** 2)

# def calculate_psnr(original, stego, max_val=32767.0):
#     mse = calculate_mse(original, stego)
#     psnr = 10 * np.log10((max_val ** 2) / mse) if mse > 0 else float('inf')
#     return psnr

# def main(cover_audio_path, stego_audio_path):
#     if not os.path.exists(cover_audio_path) or not os.path.exists(stego_audio_path):
#         print("One or both audio files do not exist.")
#         return

#     cover_audio = read_wav_file(cover_audio_path)
#     stego_audio = read_wav_file(stego_audio_path)

#     # Trim to same length
#     min_len = min(len(cover_audio), len(stego_audio))
#     cover_audio = cover_audio[:min_len]
#     stego_audio = stego_audio[:min_len]

#     snr_value = calculate_snr(cover_audio, stego_audio)
#     psnr_value = calculate_psnr(cover_audio, stego_audio)
#     mse_value = calculate_mse(cover_audio, stego_audio)

#     print(f"SNR   : {snr_value:.2f} dB")
#     print(f"PSNR  : {psnr_value:.2f} dB")
#     print(f"MSE   : {mse_value:.4f}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python quality.py <cover_audio.wav> <stego_audio.wav>")
#     else:
#         main(sys.argv[1], sys.argv[2])



import numpy as np
from scipy.io import wavfile
import os

def to_mono(audio):
    """
    Convert stereo audio to mono by averaging channels.
    """
    if len(audio.shape) == 2:
        return audio.mean(axis=1)
    return audio

def calculate_mse(original, stego):
    """
    Mean Squared Error between original and stego audio.
    """
    return np.mean((original - stego) ** 2)

def calculate_psnr(mse, max_pixel=32767.0):
    """
    Peak Signal-to-Noise Ratio based on MSE.
    """
    if mse == 0:
        return float('inf')
    return 20 * np.log10(max_pixel / np.sqrt(mse))

def calculate_snr(signal, noise):
    """
    Signal-to-Noise Ratio.
    """
    signal_power = np.mean(signal ** 2)
    noise_power = np.mean(noise ** 2)
    if noise_power == 0:
        return float('inf')
    return 10 * np.log10(signal_power / noise_power)

def check_quality(original_path, stego_path):
    if not os.path.exists(original_path):
        print("Original file does not exist.")
        return
    if not os.path.exists(stego_path):
        print("Stego file does not exist.")
        return

    sr1, original_audio = wavfile.read(original_path)
    sr2, stego_audio = wavfile.read(stego_path)

    if sr1 != sr2:
        print("Sample rates do not match.")
        return

    # Convert to mono
    original_audio = to_mono(original_audio)
    stego_audio = to_mono(stego_audio)

    # Clip to same length
    min_len = min(len(original_audio), len(stego_audio))
    original_audio = original_audio[:min_len]
    stego_audio = stego_audio[:min_len]

    # Convert to float for computation
    original_audio = original_audio.astype(np.float64)
    stego_audio = stego_audio.astype(np.float64)

    # Compute noise
    noise = original_audio - stego_audio

    # Calculate metrics
    mse = calculate_mse(original_audio, stego_audio)
    psnr = calculate_psnr(mse)
    snr = calculate_snr(original_audio, noise)

    print(f"\n--- Quality Metrics ---")
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Peak Signal-to-Noise Ratio (PSNR): {psnr:.2f} dB")
    print(f"Signal-to-Noise Ratio (SNR): {snr:.2f} dB")

if __name__ == "__main__":
    original_file = input("Enter the path to original WAV file: ")
    stego_file = input("Enter the path to stego WAV file: ")
    check_quality(original_file, stego_file)
