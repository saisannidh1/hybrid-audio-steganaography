
import numpy as np
import scipy.io.wavfile as wavfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64
import random

# --- Helper Functions ---

def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def split_into_n_parts(binary_message, n):
    part_size = len(binary_message) // n
    parts = [binary_message[i*part_size : (i+1)*part_size] for i in range(n-1)]
    parts.append(binary_message[(n-1)*part_size:])
    return parts

def generate_salt_from_audio(audio):
    salt = hashlib.sha256(audio.tobytes()).hexdigest()
    return salt

def encrypt_key(key, password):
    password_hash = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(password_hash, AES.MODE_CBC)
    encrypted_key = cipher.encrypt(pad(key.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + encrypted_key).decode()

def decrypt_key(enc_key_b64, password):
    enc_key = base64.b64decode(enc_key_b64)
    iv = enc_key[:AES.block_size]
    encrypted_key = enc_key[AES.block_size:]
    password_hash = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(password_hash, AES.MODE_CBC, iv)
    decrypted_key = unpad(cipher.decrypt(encrypted_key), AES.block_size).decode()
    return decrypted_key

# --- Encoding Methods ---

def phase_encode_part(audio, binary_message, segment_length=8192, start_sample=0):
    modified_audio = audio.copy().astype(float)
    for i in range(len(binary_message)):
        start = start_sample + i * segment_length
        end = start + segment_length
        if end > len(audio):
            break
        segment = audio[start:end]
        fft_data = np.fft.fft(segment)
        phase = np.angle(fft_data)
        magnitude = np.abs(fft_data)
        if binary_message[i] == '1':
            phase[10:21] = np.pi / 2
        else:
            phase[10:21] = -np.pi / 2
        fft_modified = magnitude * np.exp(1j * phase)
        modified_segment = np.fft.ifft(fft_modified).real
        modified_audio[start:end] = modified_segment
    return modified_audio

def lsb_encode_part(audio, binary_message, start_sample=0):
    modified_audio = np.copy(audio)
    for i in range(len(binary_message)):
        index = start_sample + i
        if index >= len(audio):
            print(f"Warning: Audio too short for LSB encoding at sample {index}")
            break
        modified_audio[index] = (modified_audio[index] & ~1) | int(binary_message[i])
    return modified_audio

# --- Decoding Methods ---

def phase_decode_part(audio, part_length, segment_length=8192, start_sample=0):
    binary_message = ''
    for i in range(part_length):
        start = start_sample + i * segment_length
        end = start + segment_length
        if end > len(audio):
            break
        segment = audio[start:end]
        fft_data = np.fft.fft(segment)
        phase = np.angle(fft_data)
        # Use threshold to be more robust against small noise
        avg_phase = np.mean(phase[10:21])
        if avg_phase > 0:
            binary_message += '1'
        else:
            binary_message += '0'
    return binary_message

def lsb_decode_part(audio, part_length, start_sample=0):
    binary_message = ''
    for i in range(part_length):
        index = start_sample + i
        if index >= len(audio):
            break
        binary_message += str(audio[index] & 1)
    return binary_message

# --- Hybrid Encoding/Decoding ---

def generate_method_sequence(seed, n):
    random.seed(seed)
    return [random.choice(['LSB', 'PHASE']) for _ in range(n)]

def hybrid_encode_n(input_wav, output_wav, message, n=4, segment_length=8192, password="strongpassword"):
    message = message.strip()
    binary_message = text_to_bits(message)
    message_length = len(binary_message)
    print(f"Message: '{message}', length: {len(message)} chars, {message_length} bits")

    parts = split_into_n_parts(binary_message, n)

    sample_rate, audio = wavfile.read(input_wav)
    if len(audio.shape) > 1:
        audio = audio[:, 0]  # Take only first channel if stereo
    if audio.dtype != np.int16:
        audio = np.int16(audio)

    salt = generate_salt_from_audio(audio)
    seed_material = hashlib.sha256((salt + password).encode()).hexdigest()
    method_sequence = generate_method_sequence(seed_material, n)

    required_samples = sum([
        len(part) * segment_length if method == 'PHASE' else len(part)
        for part, method in zip(parts, method_sequence)
    ])
    if len(audio) < required_samples:
        raise ValueError(f"Audio too short: {len(audio)} samples, need {required_samples}")

    modified_audio = np.copy(audio)
    modified_audio_float = modified_audio.astype(float)
    start_sample = 0

    for part, method in zip(parts, method_sequence):
        if method == 'PHASE':
            modified_audio_float = phase_encode_part(modified_audio_float, part, segment_length, start_sample)
            start_sample += len(part) * segment_length
        else:
            modified_audio = np.int16(modified_audio_float)
            modified_audio = lsb_encode_part(modified_audio, part, start_sample)
            modified_audio_float = modified_audio.astype(float)
            start_sample += len(part)

    modified_audio = np.int16(modified_audio_float)
    modified_audio[start_sample:] = modified_audio[start_sample:] & ~1

    max_amplitude = np.max(np.abs(modified_audio))
    if max_amplitude > 32767:
        modified_audio = np.int16(modified_audio * 32767 / max_amplitude)

    key = f"{salt}|{n}|{message_length}"
    encrypted_key = encrypt_key(key, password)

    wavfile.write(output_wav, sample_rate, modified_audio)
    return encrypted_key

def hybrid_decode_n(input_wav, encrypted_key, password="strongpassword", segment_length=8192):
    decrypted_key = decrypt_key(encrypted_key, password)
    salt, n, message_length = decrypted_key.split('|')
    n = int(n)
    message_length = int(message_length)

    print(f"Decrypted key: salt={salt}, n={n}, message_length={message_length} bits")

    seed_material = hashlib.sha256((salt + password).encode()).hexdigest()
    method_sequence = generate_method_sequence(seed_material, n)

    sample_rate, audio = wavfile.read(input_wav)
    if len(audio.shape) > 1:
        audio = audio[:, 0]

    start_sample = 0
    binary_message = ''
    part_size = message_length // n
    part_lengths = [part_size] * (n - 1) + [message_length - part_size * (n - 1)]

    for part_len, method in zip(part_lengths, method_sequence):
        if method == 'PHASE':
            part_bits = phase_decode_part(audio, part_len, segment_length, start_sample)
            start_sample += part_len * segment_length
        else:
            part_bits = lsb_decode_part(audio, part_len, start_sample)
            start_sample += part_len
        binary_message += part_bits

    message = bits_to_text(binary_message)
    return message

# --- Example Usage ---

if __name__ == "__main__":
    mode = input("Enter E to encode or D to decode: ").strip().upper()

    if mode == 'E':
        input_wav = input("Enter input WAV file path: ")
        output_wav = input("Enter output stego WAV file path: ")
        secret_message = input("Enter the secret message: ")
        n = int(input("Enter number of parts (n): "))
        password = input("Enter encryption password: ")

        encrypted_key = hybrid_encode_n(input_wav, output_wav, secret_message, n, password=password)
        print(f"Encrypted key: {encrypted_key}")
        print("Save this key for decoding.")

    elif mode == 'D':
        stego_wav = input("Enter stego WAV file path: ")
        encrypted_key = input("Enter the key: ")
        password = input("Enter decryption password: ")

        message = hybrid_decode_n(stego_wav, encrypted_key, password=password)
        print(f"Decoded message: {message}")
