import PyPDF2
import re
import sys
import os
import random
import math
import shutil
import unicodedata

def remove_accents(text):
    # Normalize text to decompose characters into base letter and diacritical marks
    nfkd_form = unicodedata.normalize('NFKD', text)
    # Remove diacritical marks but keep base letters
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_text(text):
    # Convert all text to lowercase
    text = text.lower()
    
    # Remove accents but keep base letters
    text = remove_accents(text)
    
    # Remove all characters except letters, numbers and spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove line breaks
    text = text.replace('\n', ' ')
    
    # Replace remaining single spaces with underscores
    text = text.replace(' ', '_')
    
    return text

def clean_filename(filename):
    # Remove extension
    filename = os.path.splitext(filename)[0]
    # Convert to lowercase
    filename = filename.lower()
    # Remove accents but keep base letters
    filename = remove_accents(filename)
    # Remove all characters except letters and spaces
    filename = re.sub(r'[^a-z\s]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    return filename

def convert_pdf_to_clean_text(pdf_path, texts_dir):
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Clean the text according to specifications
            cleaned_text = clean_text(text)
            
            # Create clean output filename
            base_filename = os.path.basename(pdf_path)
            clean_name = clean_filename(base_filename)
            output_filename = os.path.join(texts_dir, f"{clean_name}_clean.txt")
            
            # Write the cleaned text to a file
            with open(output_filename, 'w', encoding='utf-8') as output_file:
                output_file.write(cleaned_text)
            
            print(f"Converted successfully: {base_filename} -> {os.path.basename(output_filename)}")
            
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")

def process_directory(directory_path):
    # Create texts directory if it doesn't exist
    texts_dir = os.path.join(directory_path, 'texts')
    os.makedirs(texts_dir, exist_ok=True)
    
    # Counter for processed files
    processed = 0
    errors = 0
    
    # Process all PDF files in the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            try:
                convert_pdf_to_clean_text(pdf_path, texts_dir)
                processed += 1
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                errors += 1
    
    # Print summary
    print(f"\nProcessamento concluído:")
    print(f"- {processed} arquivos processados com sucesso")
    print(f"- {errors} arquivos com erro")
    if processed == 0 and errors == 0:
        print("Nenhum arquivo PDF encontrado no diretório!")
    
    return texts_dir

def create_batches(texts_dir, batch_size=100000):
    # Read and concatenate all text files
    all_text = ""
    for filename in os.listdir(texts_dir):
        if filename.endswith('_clean.txt'):
            with open(os.path.join(texts_dir, filename), 'r', encoding='utf-8') as f:
                all_text += f.read()
    
    total_chars = len(all_text)
    print(f"\nTotal de caracteres: {total_chars}")
    
    # Split text into batches
    batches = []
    start = 0
    while start < len(all_text):
        end = start + batch_size
        if end > len(all_text):
            end = len(all_text)
        batches.append(all_text[start:end])
        start = end
    
    print(f"Número de batches criados: {len(batches)}")
    return batches

def create_train_test_valid_split(batches, output_dir):
    # Create output directories
    splits_dir = os.path.join(output_dir, 'splits')
    train_dir = os.path.join(splits_dir, 'train')
    test_dir = os.path.join(splits_dir, 'test')
    valid_dir = os.path.join(splits_dir, 'valid')
    
    # Remove if exists and create new directories
    if os.path.exists(splits_dir):
        shutil.rmtree(splits_dir)
    
    os.makedirs(train_dir)
    os.makedirs(test_dir)
    os.makedirs(valid_dir)
    
    # Shuffle batches
    random.shuffle(batches)
    
    # Calculate split sizes
    total_batches = len(batches)
    train_size = math.floor(total_batches * 0.8)
    test_size = math.floor(total_batches * 0.1)
    valid_size = total_batches - train_size - test_size
    
    # Split batches
    train_batches = batches[:train_size]
    test_batches = batches[train_size:train_size + test_size]
    valid_batches = batches[train_size + test_size:]
    
    # Save batches
    def save_batches(batches, directory, prefix):
        for i, batch in enumerate(batches):
            filename = os.path.join(directory, f"{prefix}_batch_{i+1}.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(batch)
    
    save_batches(train_batches, train_dir, 'train')
    save_batches(test_batches, test_dir, 'test')
    save_batches(valid_batches, valid_dir, 'valid')
    
    print(f"\nDivisão dos batches:")
    print(f"- Train: {len(train_batches)} batches")
    print(f"- Test: {len(test_batches)} batches")
    print(f"- Valid: {len(valid_batches)} batches")
    print(f"\nArquivos salvos em: {splits_dir}")

def process_and_split_texts(directory_path):
    # First process all PDFs
    texts_dir = process_directory(directory_path)
    
    # Create batches
    batches = create_batches(texts_dir)
    
    # Create train/test/valid split
    create_train_test_valid_split(batches, directory_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_clean_text.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' não é um diretório válido.")
        sys.exit(1)
    
    process_and_split_texts(directory_path) 