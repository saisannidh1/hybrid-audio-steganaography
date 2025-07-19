# Hybrid Audio Steganography with LSB and Phase Coding

This project implements a hybrid audio steganography system that securely embeds secret messages within `.wav` audio files. It combines two distinct techniques—Least Significant Bit (LSB) encoding and Phase Coding—to achieve both high data capacity and robustness. The system features a password-based security mechanism using AES encryption to protect the decoding key, ensuring that only authorized users can retrieve the hidden information. A user-friendly graphical interface (GUI) is provided for easy encoding and decoding operations.

## Features

-   **Hybrid Steganography:** Employs a combination of LSB and Phase Coding for embedding data.
-   **Password-Based Security:** Encrypts the decoding key using AES with a user-provided password.
-   **Dynamic Method Selection:** The secret message is split into `n` parts, and the encoding method (LSB or Phase) for each part is chosen pseudo-randomly based on a seed derived from the audio file and the password.
-   **Graphical User Interface:** A simple Tkinter-based GUI facilitates easy interaction for encoding and decoding tasks.
-   **Imperceptibility Analysis:** Includes tools to measure the quality of the stego-audio using metrics like Peak Signal-to-Noise Ratio (PSNR), Signal-to-Noise Ratio (SNR), and Mean Squared Error (MSE).
-   [cite_start]**Visual Comparison:** Provides a script to plot and compare the waveforms and spectrograms of the original and stego-audio files for visual analysis.

## How It Works

The system's methodology is divided into two main processes: encoding and decoding.

### Encoding Process

1.  **Input:** The user provides a cover `.wav` file, a secret message, the number of parts (`n`) to split the message into, and a password.
2.  **Message Preparation:** The text message is converted into a binary string and divided into `n` segments.
3.  **Method Sequencing:** A unique salt is generated from the cover audio's content using a SHA-256 hash. This salt, combined with the user's password, seeds a random generator that produces a sequence of `n` encoding methods ('LSB' or 'PHASE'). This ensures the method sequence is unique for each audio/password pair.
4.  **Embedding:** The system iterates through the message parts, embedding each one into a distinct section of the audio using the corresponding method from the generated sequence.
5.  **Key Generation & Encryption:** A key is constructed containing the salt, the number of parts `n`, and the total message length. This key is then encrypted using AES in CBC mode with the user's password.
6.  **Output:** The modified audio is saved as a new `stego.wav` file in the `encoded_outputs` directory. The base64-encoded encrypted key is returned to the user and automatically appended to `keys.txt`.

### Decoding Process

1.  **Input:** The user provides the stego `.wav` file, the encrypted key, and the correct password.
2.  **Key Decryption:** The system uses the password to decrypt the AES-encrypted key, revealing the original salt, `n`, and message length.
3.  **Method Recreation:** The salt and password are used to regenerate the exact same sequence of encoding methods that was used during the encoding phase.
4.  **Extraction:** The system reads the stego-audio and extracts the binary message parts sequentially, applying the correct decoding algorithm (LSB or Phase) for each part according to the regenerated method sequence.
5.  **Output:** The binary parts are reassembled, converted back into text, and displayed to the user.

## Quality Metrics

The quality and imperceptibility of the steganography can be assessed using the `quality.py` script. It calculates the following standard metrics:

-   **Mean Squared Error (MSE):** Measures the average of the squared differences between the original and stego signals. A lower MSE indicates less error.
    $$MSE = \frac{1}{N} \sum_{i=1}^{N} (S_{original}[i] - S_{stego}[i])^2$$

-   **Peak Signal-to-Noise Ratio (PSNR):** The ratio between the maximum possible power of a signal and the power of the noise affecting it. A higher PSNR value indicates better quality. The formula used is:
    $$PSNR = 20 \cdot \log_{10}\left(\frac{MAX_I}{\sqrt{MSE}}\right)$$
    where $MAX_I$ is the maximum possible amplitude for the audio type (e.g., 32767 for 16-bit PCM audio).

-   **Signal-to-Noise Ratio (SNR):** Compares the power of the original signal to the power of the noise (the difference between original and stego signals).
    $$SNR = 10 \cdot \log_{10}\left(\frac{P_{signal}}{P_{noise}}\right)$$
    where $P$ is the average power.

## Technologies Used

-   Python 3
-   [cite_start]NumPy 
-   [cite_start]SciPy 
-   Tkinter
-   PyCryptodome
-   [cite_start]Matplotlib 

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/saisannidh1/Hybrid-Audio-Steganography.git](https://github.com/saisannidh1/Hybrid-Audio-Steganography.git)
    cd Hybrid-Audio-Steganography
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install numpy scipy pycryptodomex matplotlib
    ```

## How to Use

### Main Application (`gui.py`)

To start the graphical user interface, run:
```bash
python gui.py
