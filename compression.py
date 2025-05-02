import os
import math
import lzma
import zlib
import numpy as np
from collections import Counter
import pandas as pd

from ppm.main import main

def load_text(filepath):
    """Load text from a file."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def calculate_entropy(text):
    """Calculate Shannon entropy of a text."""
    counter = Counter(text)
    length = len(text)
    probabilities = [count / length for count in counter.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy

def calculate_binary_entropy(data):
    """Calculate Shannon entropy of binary data."""
    counter = Counter(data)
    length = len(data)
    probabilities = [count / length for count in counter.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy

def calculate_compressor_entropy(text, compression_func):
    """
    Estimate the entropy of a compression algorithm by comparing
    original size to compressed size.
    
    Args:
        text: The input text
        compression_func: Function that takes text and returns compressed data
    
    Returns:
        Entropy estimate in bits per symbol
    """
    text_bytes = text.encode('utf-8')
    text_length = len(text_bytes)
    
    # Split text into chunks to analyze compression patterns
    # We'll use chunks of different sizes to get a better estimate
    chunk_sizes = [100, 200, 500, 1000, 2000, 5000]
    bits_per_symbol_values = []
    
    for chunk_size in chunk_sizes:
        if chunk_size > text_length:
            continue
            
        chunks = [text_bytes[i:i+chunk_size] for i in range(0, text_length, chunk_size) if i+chunk_size <= text_length]
        
        if not chunks:
            continue
            
        compressed_sizes = []
        for chunk in chunks:
            compressed = compression_func(chunk.decode('utf-8', errors='ignore'))
            if isinstance(compressed, tuple):
                # If compression_func returns (compressed_data, ratio)
                compressed = compressed[0]
            compressed_sizes.append(len(compressed))
        
        # Calculate average compression ratio and convert to bits per symbol
        avg_compressed_size = sum(compressed_sizes) / len(compressed_sizes)
        avg_bits_per_symbol = (avg_compressed_size * 8) / chunk_size
        bits_per_symbol_values.append(avg_bits_per_symbol)
    
    if not bits_per_symbol_values:
        return 0
        
    # Return average bits per symbol across different chunk sizes
    return sum(bits_per_symbol_values) / len(bits_per_symbol_values)

def calculate_avg_sequence_length(text, compression_func):
    """
    Estima o comprimento médio das sequências geradas pelo compressor
    analisando a compressão em trechos de texto de diferentes tamanhos.
    
    Args:
        text: O texto de entrada
        compression_func: Função que comprime o texto
        
    Returns:
        Comprimento médio da sequência em bytes
    """
    # Vamos comprimir trechos de texto e analisar os padrões de repetição
    text_bytes = text.encode('utf-8')
    
    # Tamanhos variados para análise
    chunk_sizes = [1000, 2000, 5000]
    sequence_lengths = []
    
    for chunk_size in chunk_sizes:
        if len(text_bytes) < chunk_size:
            continue
            
        # Pega um trecho do texto
        chunk = text_bytes[:chunk_size]
        
        # Comprime o trecho
        compressed = compression_func(chunk.decode('utf-8', errors='ignore'))
        if isinstance(compressed, tuple):
            compressed = compressed[0]
            
        # Identifica sequências de bytes repetidos (aproximação)
        sequences = []
        current_seq = [compressed[0]]
        
        for i in range(1, len(compressed)):
            # Se o byte atual é uma continuação da sequência
            if abs(compressed[i] - compressed[i-1]) <= 5:  # Tolerância para aproximação
                current_seq.append(compressed[i])
            else:
                # Nova sequência
                if len(current_seq) > 1:  # Apenas sequências com mais de um byte
                    sequences.append(current_seq)
                current_seq = [compressed[i]]
        
        # Adiciona a última sequência, se existir
        if len(current_seq) > 1:
            sequences.append(current_seq)
            
        # Calcula o comprimento médio das sequências
        if sequences:
            avg_length = sum(len(seq) for seq in sequences) / len(sequences)
            sequence_lengths.append(avg_length)
    
    if not sequence_lengths:
        return 0
    
    return sum(sequence_lengths) / len(sequence_lengths)

def calculate_avg_length(text):
    """Calculate average length of words in a text."""
    words = text.split()
    if not words:
        return 0
    return sum(len(word) for word in words) / len(words)

def compress_lzma(text):
    """Compress text using LZMA algorithm."""
    text_bytes = text.encode('utf-8')
    compressed = lzma.compress(text_bytes)
    return compressed, len(compressed) / len(text_bytes)

def compress_zlib(text):
    """Compress text using zlib (LZ77)."""
    text_bytes = text.encode('utf-8')
    compressed = zlib.compress(text_bytes)
    return compressed, len(compressed) / len(text_bytes)

def bwt_transform(text):
    """Perform Burrows-Wheeler Transform on text."""
    # Add a sentinel character to mark the end of the text
    text = text + '$'
    
    # Generate all rotations of the text
    rotations = [text[i:] + text[:i] for i in range(len(text))]
    
    # Sort the rotations
    sorted_rotations = sorted(rotations)
    
    # Extract the last column of the sorted rotations
    bwt = ''.join(rotation[-1] for rotation in sorted_rotations)
    
    # Find the index of the original text in the sorted rotations
    index = sorted_rotations.index(text)
    
    return bwt, index

def bwt_inverse(bwt, index):
    """Invert the Burrows-Wheeler Transform."""
    # Initialize an empty list for storing the sorted rotations
    table = [''] * len(bwt)
    
    # Build the table by adding characters to the beginning of each rotation
    for i in range(len(bwt)):
        table = sorted([bwt[j] + table[j] for j in range(len(bwt))])
    
    # Return the original text (removing the sentinel character)
    return table[index][:-1]

def run_compression_analysis(filepath, i):
    """Run comprehensive compression analysis on a file."""
    print(f"Analyzing file: {filepath}")
    Textos = []
    Textos.append("train_batch_" + str(i) + ".txt")

    # Load text
    text = load_text(filepath)
    print(f"Text length: {len(text)} characters")
    
    # Run PPM compression
    print("\nPPM compression:")
    ppm_entropy, ppm_avg_seq_length = main(filepath)
    print(f"PPM entropy estimate: {ppm_entropy:.4f} bits per symbol")
    print(f"PPM avg sequence length: {ppm_avg_seq_length:.4f} bytes")

    # Calculate basic text statistics
    entropy = calculate_entropy(text)
    avg_length = calculate_avg_length(text)
    print(f"Shannon Entropy: {entropy:.4f} bits per symbol")
    print(f"Average word length: {avg_length:.4f} characters")
    
    # Calculate theoretical minimum size based on entropy
    theoretical_min_size = (entropy * len(text)) / 8  # Convert bits to bytes
    print(f"Theoretical minimum size (based on entropy): {theoretical_min_size:.2f} bytes")
    
    # Calculate entropy for each compressor
    # We'll use a sample of the text for computational efficiency
    sample_text = text[:20000]  # Use a 20K sample
    
    # LZMA entropy estimation
    lzma_entropy = calculate_compressor_entropy(sample_text, compress_lzma)
    lzma_avg_seq_length = calculate_avg_sequence_length(sample_text, compress_lzma)
    
    # LZ77 entropy estimation  
    lz77_entropy = calculate_compressor_entropy(sample_text, compress_zlib)
    lz77_avg_seq_length = calculate_avg_sequence_length(sample_text, compress_zlib)
    
    # LZMA Compression
    print("\nLZMA Compression:")
    lzma_compressed, lzma_ratio = compress_lzma(text)
    print(f"Compressed size: {len(lzma_compressed)} bytes")
    print(f"Compression ratio: {lzma_ratio:.4f}")
    print(f"Space saving: {(1 - lzma_ratio) * 100:.2f}%")
    print(f"LZMA entropy estimate: {lzma_entropy:.4f} bits per symbol")
    print(f"LZMA avg sequence length: {lzma_avg_seq_length:.4f} bytes")
    
    # LZ77 (zlib) Compression
    print("\nLZ77 (zlib) Compression:")
    zlib_compressed, zlib_ratio = compress_zlib(text)
    print(f"Compressed size: {len(zlib_compressed)} bytes")
    print(f"Compression ratio: {zlib_ratio:.4f}")
    print(f"Space saving: {(1 - zlib_ratio) * 100:.2f}%")
    print(f"LZ77 entropy estimate: {lz77_entropy:.4f} bits per symbol")
    print(f"LZ77 avg sequence length: {lz77_avg_seq_length:.4f} bytes")
    '''
    # BWT and compression
    print("\nBurrows-Wheeler Transform (BWT):")
    try:
        # Limit BWT to first 10,000 characters to avoid memory issues
        sample_text = text[:10000]
        bwt_text, bwt_index = bwt_transform(sample_text)
        
        # Calculate BWT entropy
        bwt_entropy = calculate_entropy(bwt_text)
        
        # Verify BWT by inverse
        reconstructed = bwt_inverse(bwt_text, bwt_index)
        is_correct = reconstructed == sample_text
        
        # Calculate run-length characteristics
        run_lengths = []
        current_char = bwt_text[0]
        current_run = 1
        
        for char in bwt_text[1:]:
            if char == current_char:
                current_run += 1
            else:
                run_lengths.append(current_run)
                current_char = char
                current_run = 1
        
        run_lengths.append(current_run)
        
        print(f"BWT sample size: {len(sample_text)} characters")
        print(f"BWT index: {bwt_index}")
        print(f"BWT entropy: {bwt_entropy:.4f} bits per symbol")
        print(f"Average run length: {np.mean(run_lengths):.4f}")
        print(f"Max run length: {max(run_lengths)}")
        print(f"BWT validation: {'Successful' if is_correct else 'Failed'}")
        
        # Compress BWT output and calculate entropy
        # First with LZMA
        bwt_lzma_compressed, bwt_lzma_ratio = compress_lzma(bwt_text)
        bwt_lzma_entropy = calculate_compressor_entropy(bwt_text, compress_lzma)
        bwt_lzma_avg_seq_length = calculate_avg_sequence_length(bwt_text, compress_lzma)
        print(f"BWT+LZMA size: {len(bwt_lzma_compressed)} bytes")
        print(f"BWT+LZMA ratio: {bwt_lzma_ratio:.4f}")
        print(f"BWT+LZMA entropy estimate: {bwt_lzma_entropy:.4f} bits per symbol")
        print(f"BWT+LZMA avg sequence length: {bwt_lzma_avg_seq_length:.4f} bytes")
        
        # Then with LZ77
        bwt_zlib_compressed, bwt_zlib_ratio = compress_zlib(bwt_text)
        bwt_lz77_entropy = calculate_compressor_entropy(bwt_text, compress_zlib)
        bwt_lz77_avg_seq_length = calculate_avg_sequence_length(bwt_text, compress_zlib)
        print(f"BWT+LZ77 size: {len(bwt_zlib_compressed)} bytes")
        print(f"BWT+LZ77 ratio: {bwt_zlib_ratio:.4f}")
        print(f"BWT+LZ77 entropy estimate: {bwt_lz77_entropy:.4f} bits per symbol")
        print(f"BWT+LZ77 avg sequence length: {bwt_lz77_avg_seq_length:.4f} bytes")
    except Exception as e:
        print(f"BWT analysis failed: {e}")
    '''

    print("\nCompression Summary:")
    print(f"Original size: {len(text.encode('utf-8'))} bytes")
    print(f"Original entropy: {entropy:.4f} bits per symbol")
    print(f"LZMA: {len(lzma_compressed)} bytes ({(1 - lzma_ratio) * 100:.2f}% saving)")
    print(f"LZMA entropy estimate: {lzma_entropy:.4f} bits per symbol")
    print(f"LZMA avg sequence length: {lzma_avg_seq_length:.4f} bytes")
    print(f"LZ77: {len(zlib_compressed)} bytes ({(1 - zlib_ratio) * 100:.2f}% saving)")
    print(f"LZ77 entropy estimate: {lz77_entropy:.4f} bits per symbol")
    print(f"LZ77 avg sequence length: {lz77_avg_seq_length:.4f} bytes")
    '''
    if 'bwt_entropy' in locals():
        print(f"BWT entropy: {bwt_entropy:.4f} bits per symbol")
        print(f"BWT+LZMA entropy estimate: {bwt_lzma_entropy:.4f} bits per symbol")
        print(f"BWT+LZMA avg sequence length: {bwt_lzma_avg_seq_length:.4f} bytes")
        print(f"BWT+LZ77 entropy estimate: {bwt_lz77_entropy:.4f} bits per symbol")
        print(f"BWT+LZ77 avg sequence length: {bwt_lz77_avg_seq_length:.4f} bytes")
    '''

    return {
        "ppm_entropy": ppm_entropy,
        "ppm_avg_length": ppm_avg_seq_length,
        "lzma_entropy": lzma_entropy,
        "lzma_avg_seq_length": lzma_avg_seq_length,
        "lz77_entropy": lz77_entropy,
        "lz77_avg_seq_length": lz77_avg_seq_length
    }

if __name__ == "__main__":
    # Set the filepath to the text file
    # Run the analysis
    
    for i in range(1, 5):
        if i == 1:
            regiao = "nordeste"
        if i == 2:
            regiao = "norte"
        if i == 3:
            regiao = "sul"
        if i == 4:
            regiao = "sudeste"
        
        print(f"Running analysis for {regiao} region")

        txts = []
        ppm_entropy = []
        ppm_avg_length = []
        lzma_entropy = []
        lzma_avg_length = []
        lz77_entropy = []
        lz77_avg_length = []

        for i in range(1, 4):
            filepath = "db/"+regiao+"/splits/train/train_batch_"+  str(i) + ".txt"
            results = run_compression_analysis(filepath, i)
            txts.append("train_batch_" + str(i) + ".txt")
            ppm_entropy.append(results["ppm_entropy"])
            ppm_avg_length.append(results["ppm_avg_length"])
            lzma_entropy.append(results["lzma_entropy"])
            lzma_avg_length.append(results["lzma_avg_seq_length"])
            lz77_entropy.append(results["lz77_entropy"])
            lz77_avg_length.append(results["lz77_avg_seq_length"])
        # Save results to a CSV file
        df = pd.DataFrame({
            "Text": txts,
            "PPM Entropy": ppm_entropy,
        })
        df.to_csv("results/"+regiao+"/ppm_entropy.csv", index=False)
        df = pd.DataFrame({
            "Text": txts,
            "PPM Avg Length": ppm_avg_length,
        })
        df.to_csv("results/"+regiao+"/ppm_avg_length.csv", index=False)
        df = pd.DataFrame({
            "Text": txts,
            "LZMA Entropy": lzma_entropy,
        })
        df.to_csv("results/"+regiao+"/lzma_entropy.csv", index=False)
        df = pd.DataFrame({
            "Text": txts,
            "LZMA Avg Length": lzma_avg_length,
        })
        df.to_csv("results/"+regiao+"/lzma_avg_length.csv", index=False)
        df = pd.DataFrame({
            "Text": txts,
            "LZ77 Entropy": lz77_entropy,
        })
        df.to_csv("results/"+regiao+"/lz77_entropy.csv", index=False)
        df = pd.DataFrame({
            "Text": txts,
            "LZ77 Avg Length": lz77_avg_length,
        })
        df.to_csv("results/"+regiao+"/lz77_avg_length.csv", index=False)
        #.csv com as medias
        ppm_entropy_mean = np.mean(ppm_entropy)
        ppm_avg_length_mean = np.mean(ppm_avg_length)
        lzma_entropy_mean = np.mean(lzma_entropy)
        lzma_avg_length_mean = np.mean(lzma_avg_length)
        lz77_entropy_mean = np.mean(lz77_entropy)
        lz77_avg_length_mean = np.mean(lz77_avg_length)
        df = pd.DataFrame({
            "Text": ["mean_"+regiao],
            "PPM Entropy": [ppm_entropy_mean],
            "PPM Avg Length": [ppm_avg_length_mean],
            "LZMA Entropy": [lzma_entropy_mean],
            "LZMA Avg Length": [lzma_avg_length_mean],
            "LZ77 Entropy": [lz77_entropy_mean],
            "LZ77 Avg Length": [lz77_avg_length_mean]
        })
        df.to_csv("results/"+regiao+"/mean.csv", index=False)
        print(f"Results saved to results/{regiao}/")
