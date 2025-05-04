import os
import math
import lzma
import zlib
import numpy as np
from collections import Counter
import pandas as pd
from pathlib import Path

# Constants for the analysis
REGIONS = ["nordeste", "norte", "sul", "sudeste"]
SPLIT_TYPES = ["train", "valid", "test"]

def load_text(filepath):
    """Load text from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error loading file {filepath}: {e}")
        return ""

def calculate_entropy(text):
    """Calculate Shannon entropy of a text."""
    counter = Counter(text)
    length = len(text)
    probabilities = [count / length for count in counter.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy

def static_compress(text, model_text):
    """
    Compress text using a static model built from model_text.
    Returns compressed data and compression ratio.
    """
    # Build static model (character frequency distribution)
    model_counter = Counter(model_text)
    model_length = len(model_text)
    model_probs = {char: count/model_length for char, count in model_counter.items()}
    
    # Calculate expected code length for each character based on the model
    # Using Shannon's formula: -log2(p) bits for a character with probability p
    model_codes = {char: -math.log2(prob) for char, prob in model_probs.items()}
    
    # Calculate the total bits needed to encode the text with the static model
    total_bits = 0
    unknown_char_penalty = -math.log2(1/model_length)  # Penalty for chars not in model
    
    for char in text:
        if char in model_codes:
            total_bits += model_codes[char]
        else:
            total_bits += unknown_char_penalty
    
    # Convert bits to bytes (8 bits per byte)
    compressed_size = total_bits / 8
    
    # Calculate compression ratio
    original_size = len(text.encode('utf-8'))
    compression_ratio = compressed_size / original_size
    
    return compressed_size, compression_ratio

def run_static_compression_analysis(target_region, source_region, split_type="train", batch_limit=3):
    """
    Analyze compression of texts from target_region using a static model from source_region.
    """
    print(f"Analyzing {target_region} texts using static model from {source_region}")
    
    results = []
    
    # Find all batch files in the source region to build the static model
    source_path = Path(f"db/{source_region}/splits/{split_type}")
    if not source_path.exists():
        print(f"Source path doesn't exist: {source_path}")
        return results
    
    # Load and concatenate all source texts to build the static model
    source_texts = ""
    source_files = sorted(list(source_path.glob(f"{split_type}_batch_*.txt")))[:batch_limit]
    
    if not source_files:
        print(f"No source files found in {source_path}")
        return results
    
    print(f"Building static model from {len(source_files)} files in {source_region}...")
    for src_file in source_files:
        source_texts += load_text(src_file)
    
    if not source_texts:
        print("Error: Empty source text for model building")
        return results
    
    print(f"Static model built with {len(source_texts)} characters")
    
    # Calculate entropy of the source model
    source_entropy = calculate_entropy(source_texts)
    print(f"Source model entropy: {source_entropy:.4f} bits/symbol")
    
    # Find all batch files in the target region
    target_path = Path(f"db/{target_region}/splits/{split_type}")
    if not target_path.exists():
        print(f"Target path doesn't exist: {target_path}")
        return results
    
    target_files = sorted(list(target_path.glob(f"{split_type}_batch_*.txt")))[:batch_limit]
    
    if not target_files:
        print(f"No target files found in {target_path}")
        return results
    
    # Process each target file
    for i, target_file in enumerate(target_files, 1):
        file_name = target_file.name
        print(f"Processing {file_name} ({i}/{len(target_files)})...")
        
        # Load target text
        target_text = load_text(target_file)
        if not target_text:
            print(f"Empty target text in {target_file}")
            continue
        
        # Calculate entropy of the target text
        target_entropy = calculate_entropy(target_text)
        
        # Compress using static model
        compressed_size, compression_ratio = static_compress(target_text, source_texts)
        
        # Calculate cross-entropy (bits per symbol when compressing target with source model)
        cross_entropy = (compressed_size * 8) / len(target_text)
        
        # Calculate KL divergence: cross_entropy - target_entropy
        kl_divergence = cross_entropy - target_entropy
        
        # Store results
        result = {
            "target_file": file_name,
            "target_region": target_region,
            "source_region": source_region,
            "target_entropy": target_entropy,
            "cross_entropy": cross_entropy,
            "kl_divergence": kl_divergence,
            "compression_ratio": compression_ratio
        }
        
        results.append(result)
        
        print(f"Target entropy: {target_entropy:.4f} bits/symbol")
        print(f"Cross-entropy: {cross_entropy:.4f} bits/symbol")
        print(f"KL divergence: {kl_divergence:.4f} bits/symbol")
        print(f"Compression ratio: {compression_ratio:.4f}")
        print("-" * 50)
    
    return results

def analyze_all_regions(split_type="train", batch_limit=3):
    """Run analysis for all region combinations."""
    ensure_dir("results/static_compression")
    
    # For storing all results in a matrix format
    cross_entropy_matrix = pd.DataFrame(index=REGIONS, columns=REGIONS)
    kl_divergence_matrix = pd.DataFrame(index=REGIONS, columns=REGIONS)
    
    # Run analysis for each source-target region pair
    for source_region in REGIONS:
        for target_region in REGIONS:
            results = run_static_compression_analysis(
                target_region, source_region, split_type, batch_limit
            )
            
            if not results:
                print(f"No results for {source_region} -> {target_region}")
                continue
            
            # Calculate average metrics
            avg_cross_entropy = np.mean([r["cross_entropy"] for r in results])
            avg_kl_divergence = np.mean([r["kl_divergence"] for r in results])
            
            # Store in matrices
            cross_entropy_matrix.loc[target_region, source_region] = avg_cross_entropy
            kl_divergence_matrix.loc[target_region, source_region] = avg_kl_divergence
            
            # Save detailed results for this pair
            df = pd.DataFrame(results)
            df.to_csv(f"results/static_compression/{source_region}_to_{target_region}.csv", index=False)
    
    # Save matrices
    cross_entropy_matrix.to_csv(f"results/static_compression/cross_entropy_matrix.csv")
    kl_divergence_matrix.to_csv(f"results/static_compression/kl_divergence_matrix.csv")
    
    print("Analysis complete. Results saved to results/static_compression/")
    
    return cross_entropy_matrix, kl_divergence_matrix

def ensure_dir(directory):
    """Make sure a directory exists, creating it if necessary"""
    os.makedirs(directory, exist_ok=True)

if __name__ == "__main__":
    # Set the batch limit to control how many files to process per region
    BATCH_LIMIT = 3  # Process first 3 batch files from each region
    
    # Run the analysis
    cross_entropy_matrix, kl_divergence_matrix = analyze_all_regions(
        split_type="test",
        batch_limit=BATCH_LIMIT
    )
    
    # Print the matrices
    print("\nCross-Entropy Matrix:")
    print(cross_entropy_matrix)
    
    print("\nKL Divergence Matrix:")
    print(kl_divergence_matrix) 