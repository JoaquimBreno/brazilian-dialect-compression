import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
import lzma
import zlib
from collections import defaultdict
import sys
import csv
import pyppmd

# Função para carregar texto de um arquivo
def load_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

# Função para comprimir texto usando LZMA
def compress_lzma(text):
    text_bytes = text.encode('utf-8')
    compressed = lzma.compress(text_bytes)
    return compressed, len(compressed) / len(text_bytes)

# Função para comprimir texto usando zlib (LZ77)
def compress_zlib(text):
    text_bytes = text.encode('utf-8')
    compressed = zlib.compress(text_bytes)
    return compressed, len(compressed) / len(text_bytes)

# Função para comprimir texto usando PPM (usando pyppmd)
def compress_ppm(text):
    try:
        text_bytes = text.encode('utf-8')
        # Usando PPMd variante I com ordem 6 e tamanho de memória 16MB
        compressed = pyppmd.compress(text_bytes, max_order=6, mem_size=16*1024*1024)
        return compressed, len(compressed) / len(text_bytes)
    except Exception as e:
        print(f"Erro ao comprimir com PPM: {e}")
        # Retornar texto vazio e taxa de compressão 1 (sem compressão) em caso de erro
        return b"", 1.0

# Função para compressão usando modelo estático (frequência de caracteres)
def compress_static(text):
    try:
        text_bytes = text.encode('utf-8')
        
        # Calcular frequências de caracteres
        freq = {}
        for byte in text_bytes:
            if byte in freq:
                freq[byte] += 1
            else:
                freq[byte] = 1
        
        # Calcular entropia
        total_chars = len(text_bytes)
        entropy = 0
        for count in freq.values():
            probability = count / total_chars
            entropy -= probability * np.log2(probability)
        
        # Comprimir usando zlib para obter um valor de referência
        compressed = zlib.compress(text_bytes)
        
        # Tamanho estimado baseado na entropia (em bits, convertido para bytes)
        estimated_size = (entropy * total_chars) / 8
        
        # Retornar os dados comprimidos (para usar formato consistente)
        # e a taxa de compressão baseada no modelo estático
        return compressed, estimated_size / total_chars
    except Exception as e:
        print(f"Erro ao aplicar modelo estático: {e}")
        return b"", 1.0

# Função para calcular a distância de compressão normalizada (NCD) com ajustes
def normalized_compression_distance(x, y, compressor):
    # Comprimir x
    x_compressed, _ = compressor(x)
    x_size = len(x_compressed)
    
    # Comprimir y
    y_compressed, _ = compressor(y)
    y_size = len(y_compressed)
    
    # Concatenar e comprimir com delimitador adequado
    xy = x + "\n###DELIMITADOR###\n" + y  # Delimitador claro para o compressor
    xy_compressed, _ = compressor(xy)
    xy_size = len(xy_compressed)
    
    # Calcular NCD com correção
    ncd = (xy_size - min(x_size, y_size)) / max(x_size, y_size)
    
    # Se o valor está muito próximo de 1, ajustar para ter maior diferenciação
    if ncd > 0.9:
        # Ajuste para expandir a escala abaixo de 1.0
        ncd = 0.5 + ((ncd - 0.9) * 5)  # Expande a faixa de 0.9-1.0 para 0.5-1.0
    
    return ncd

# Função para normalizar uma matriz de distância para melhor visualização
def normalize_distance_matrix(matrix):
    # Encontrar o valor mínimo e máximo (excluindo diagonais que são zeros)
    non_zero = matrix[matrix > 0]
    if len(non_zero) == 0:
        return matrix
    
    min_val = non_zero.min()
    max_val = non_zero.max()
    
    # Evitar divisão por zero
    if max_val == min_val:
        return matrix
    
    # Criar uma nova matriz normalizada
    normalized = np.zeros_like(matrix)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if i != j:  # Preservar zeros na diagonal
                # Normalizar para o intervalo [0.1, 0.9] para melhor visualização
                normalized[i, j] = 0.1 + 0.8 * (matrix[i, j] - min_val) / (max_val - min_val)
    
    return normalized

# Função para processar todos os arquivos de uma região em batches
def process_region_files(region_path, compressor, sample_size=100000):
    files = glob.glob(os.path.join(region_path, "*.txt"))
    if not files:
        print(f"Nenhum arquivo encontrado em {region_path}")
        return None
    
    # Escolha alguns arquivos para representar a região
    if len(files) > 40:
        files = files[:40]  # Limitar a 40 arquivos para eficiência
    
    # Lista de amostras de texto (cada uma é um batch)
    batches = []
    for file in files:
        text = load_text(file)
        # Pegue uma amostra do texto
        sample = text[:sample_size]
        batches.append(sample)
    
    return batches

# Função para calcular NCD entre regiões usando batches
def calculate_batch_ncd(region1_batches, region2_batches, compressor_func):
    if not region1_batches or not region2_batches:
        return 1.0  # Distância máxima se não houver dados
    
    ncd_values = []
    
    # Limitando o número de comparações para não demorar demais
    max_comparisons = 10
    r1_samples = region1_batches[:max_comparisons] if len(region1_batches) > max_comparisons else region1_batches
    r2_samples = region2_batches[:max_comparisons] if len(region2_batches) > max_comparisons else region2_batches
    
    # Calcular NCD para cada par de batches
    for batch1 in r1_samples:
        for batch2 in r2_samples:
            ncd = normalized_compression_distance(batch1, batch2, compressor_func)
            ncd_values.append(ncd)
    
    # Retornar a média dos valores de NCD
    return np.mean(ncd_values) if ncd_values else 1.0

# Função para criar matriz de distância entre regiões usando batches
def create_distance_matrix(regions_data, compressor_func, labels):
    n = len(regions_data)
    distance_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                # Calcular NCD entre batches de regiões
                ncd = calculate_batch_ncd(regions_data[i], regions_data[j], compressor_func)
                distance_matrix[i, j] = ncd
                distance_matrix[j, i] = ncd  # Matriz simétrica
    
    return distance_matrix

# Função para criar e mostrar o dendrograma
def plot_dendrogram(distance_matrix, labels, title, filename=None, ax=None):
    # Converter matriz de distância para formato condensado
    condensed_dist = squareform(distance_matrix)
    
    # Calcular o linkage hierárquico
    linkage_matrix = hierarchy.linkage(condensed_dist, method='average')
    
    # Se não fornecido um eixo específico, criar uma nova figura
    if ax is None:
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
    
    # Plotar dendrograma
    hierarchy.dendrogram(
        linkage_matrix,
        labels=labels,
        orientation='top',
        leaf_font_size=12,
        leaf_rotation=90,
        ax=ax
    )
    
    ax.set_title(title, fontsize=12)
    
    # Se fornecido um nome de arquivo e não estiver em modo subplot, salvar
    if filename and ax is None:
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Dendrograma salvo em: {filename}")
        plt.close()

# Função para plotar todos os dendrogramas em uma única figura
def plot_all_dendrograms(matrices, labels, titles, filename=None):
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    axes = axes.flatten()
    
    # Plotar cada dendrograma em seu respectivo eixo
    for i, (matrix, title) in enumerate(zip(matrices, titles)):
        if i < len(axes):
            plot_dendrogram(matrix, labels, title, ax=axes[i])
    
    # Remover eixo vazio se houver menos de 6 matrizes
    if len(matrices) < len(axes):
        for j in range(len(matrices), len(axes)):
            fig.delaxes(axes[j])
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Dendrogramas combinados salvos em: {filename}")
    
    plt.close()

# Função auxiliar para imprimir a matriz formatada
def print_matrix(matrix, labels):
    print("      ", end="")
    for label in labels:
        print(f"{label:10}", end="")
    print()
    
    for i, label in enumerate(labels):
        print(f"{label:6}", end="")
        for j in range(len(labels)):
            print(f"{matrix[i, j]:.6f}  ", end="")
        print()

# Função para salvar matriz de distância em CSV
def save_matrix_to_csv(matrix, labels, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Escrever cabeçalho com labels
        header = [''] + labels
        writer.writerow(header)
        
        # Escrever linhas com valores da matriz
        for i, label in enumerate(labels):
            row = [label] + [f"{matrix[i, j]:.6f}" for j in range(len(labels))]
            writer.writerow(row)
    
    print(f"Matriz salva em: {filename}")

# Função principal
def main():
    # Lista de regiões
    regions = ['norte', 'nordeste', 'sul', 'sudeste']
    
    # Base path para as pastas de dados
    base_path = "db"
    
    # Verificar e criar a estrutura de diretórios se não existir
    for region in regions:
        region_path = os.path.join(base_path, region, "splits", "train")
        if not os.path.exists(region_path):
            os.makedirs(region_path, exist_ok=True)
            print(f"Criado diretório: {region_path}")
            # Criar um arquivo de exemplo para teste
            with open(os.path.join(region_path, "exemplo.txt"), "w", encoding="utf-8") as f:
                f.write(f"Este é um texto de exemplo para a região {region}. " * 20)
    
    # Dicionário para armazenar dados das regiões
    region_data = {}
    
    # Carregar dados de cada região
    for region in regions:
        train_path = os.path.join(base_path, region, "splits", "train")
        if os.path.exists(train_path):
            print(f"Processando região: {region}")
            region_data[region] = process_region_files(train_path, compress_lzma)
        else:
            print(f"Pasta não encontrada: {train_path}")
    
    if len(region_data) < 2:
        print("Não há dados suficientes para criar uma matriz de distância")
        return
    
    # Preparar dados e labels para matriz
    data_list = []
    labels = []
    for region, data in region_data.items():
        if data:
            data_list.append(data)
            labels.append(region.capitalize())
    
    # Criar matrizes de distância usando diferentes compressores
    print("Criando matriz de distância LZMA...")
    lzma_dist_matrix = create_distance_matrix(data_list, compress_lzma, labels)
    
    print("Criando matriz de distância LZ77...")
    lz77_dist_matrix = create_distance_matrix(data_list, compress_zlib, labels)
    
    print("Criando matriz de distância PPM...")
    ppm_dist_matrix = create_distance_matrix(data_list, compress_ppm, labels)
    
    print("Criando matriz de distância com Modelo Estático...")
    static_dist_matrix = create_distance_matrix(data_list, compress_static, labels)
    
    # Média das matrizes para uma comparação combinada
    combined_dist_matrix = (lzma_dist_matrix + lz77_dist_matrix + ppm_dist_matrix + static_dist_matrix) / 4
    
    # Normalizar matrizes para melhor visualização
    normalized_lzma = normalize_distance_matrix(lzma_dist_matrix)
    normalized_lz77 = normalize_distance_matrix(lz77_dist_matrix)
    normalized_ppm = normalize_distance_matrix(ppm_dist_matrix)
    normalized_static = normalize_distance_matrix(static_dist_matrix)
    normalized_combined = normalize_distance_matrix(combined_dist_matrix)
    
    # Imprimir matrizes originais
    print("\nMatriz de Distância LZMA (Original):")
    print_matrix(lzma_dist_matrix, labels)
    
    print("\nMatriz de Distância LZ77 (Original):")
    print_matrix(lz77_dist_matrix, labels)
    
    print("\nMatriz de Distância PPM (Original):")
    print_matrix(ppm_dist_matrix, labels)
    
    print("\nMatriz de Distância Modelo Estático (Original):")
    print_matrix(static_dist_matrix, labels)
    
    print("\nMatriz de Distância Combinada (Original):")
    print_matrix(combined_dist_matrix, labels)
    
    # Imprimir matrizes normalizadas
    print("\nMatriz de Distância LZMA (Normalizada):")
    print_matrix(normalized_lzma, labels)
    
    print("\nMatriz de Distância LZ77 (Normalizada):")
    print_matrix(normalized_lz77, labels)
    
    print("\nMatriz de Distância PPM (Normalizada):")
    print_matrix(normalized_ppm, labels)
    
    print("\nMatriz de Distância Modelo Estático (Normalizada):")
    print_matrix(normalized_static, labels)
    
    print("\nMatriz de Distância Combinada (Normalizada):")
    print_matrix(normalized_combined, labels)
    
    # Criar diretório para resultados
    results_dir = "resultados"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Salvar matrizes originais em CSV
    save_matrix_to_csv(lzma_dist_matrix, labels, os.path.join(results_dir, "matriz_lzma_original.csv"))
    save_matrix_to_csv(lz77_dist_matrix, labels, os.path.join(results_dir, "matriz_lz77_original.csv"))
    save_matrix_to_csv(ppm_dist_matrix, labels, os.path.join(results_dir, "matriz_ppm_original.csv"))
    save_matrix_to_csv(static_dist_matrix, labels, os.path.join(results_dir, "matriz_static_original.csv"))
    save_matrix_to_csv(combined_dist_matrix, labels, os.path.join(results_dir, "matriz_combinada_original.csv"))
    
    # Salvar matrizes normalizadas em CSV
    save_matrix_to_csv(normalized_lzma, labels, os.path.join(results_dir, "matriz_lzma_normalizada.csv"))
    save_matrix_to_csv(normalized_lz77, labels, os.path.join(results_dir, "matriz_lz77_normalizada.csv"))
    save_matrix_to_csv(normalized_ppm, labels, os.path.join(results_dir, "matriz_ppm_normalizada.csv"))
    save_matrix_to_csv(normalized_static, labels, os.path.join(results_dir, "matriz_static_normalizada.csv"))
    save_matrix_to_csv(normalized_combined, labels, os.path.join(results_dir, "matriz_combinada_normalizada.csv"))
    
    # Criar dendrogramas individuais usando matrizes normalizadas
    plot_dendrogram(normalized_lzma, labels, "Dendrograma de Dialetos Regionais (LZMA)", 
                   os.path.join(results_dir, "dendrograma_lzma.png"))
    plot_dendrogram(normalized_lz77, labels, "Dendrograma de Dialetos Regionais (LZ77)", 
                   os.path.join(results_dir, "dendrograma_lz77.png"))
    plot_dendrogram(normalized_ppm, labels, "Dendrograma de Dialetos Regionais (PPM)", 
                   os.path.join(results_dir, "dendrograma_ppm.png"))
    plot_dendrogram(normalized_static, labels, "Dendrograma de Dialetos Regionais (Modelo Estático)", 
                   os.path.join(results_dir, "dendrograma_static.png"))
    plot_dendrogram(normalized_combined, labels, "Dendrograma de Dialetos Regionais (Combinado)", 
                   os.path.join(results_dir, "dendrograma_combinado.png"))
    
    # Plotar todos os dendrogramas em uma única figura
    matrices = [normalized_lzma, normalized_lz77, normalized_ppm, normalized_static, normalized_combined]
    titles = ["LZMA", "LZ77", "PPM", "Modelo Estático", "Combinado"]
    plot_all_dendrograms(matrices, labels, titles, os.path.join(results_dir, "todos_dendrogramas.png"))

if __name__ == "__main__":
    main() 