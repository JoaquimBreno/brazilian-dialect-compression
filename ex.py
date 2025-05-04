import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import cm

# Simulando uma matriz de distância entre 5 regiões brasileiras
# Valores menores = maior similaridade linguística
distances = np.array([
    [0.00, 0.42, 0.65, 0.58, 0.72],  # Norte
    [0.42, 0.00, 0.52, 0.37, 0.65],  # Nordeste
    [0.65, 0.52, 0.00, 0.30, 0.45],  # Centro-Oeste
    [0.58, 0.37, 0.30, 0.00, 0.28],  # Sudeste
    [0.72, 0.65, 0.45, 0.28, 0.00]   # Sul
])

# Convertendo a matriz para um formato condensado (apenas a parte triangular superior)
condensed_distances = []
for i in range(distances.shape[0]):
    for j in range(i+1, distances.shape[0]):
        condensed_distances.append(distances[i, j])

# Aplicando clustering hierárquico
Z = linkage(condensed_distances, method='ward')

# Criando o dendrograma
plt.figure(figsize=(10, 6))
plt.title('Dendrograma de Similaridade entre Dialetos Regionais Brasileiros', fontsize=14)
plt.ylabel('Distância (Dissimilaridade)', fontsize=12)
plt.xlabel('Regiões', fontsize=12)

dendrogram(
    Z,
    labels=['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'],
    leaf_rotation=90,
    leaf_font_size=12,
    color_threshold=0.5,  # Define onde as cores mudam
)

plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7)  # Linha de corte para mostrar clusters
plt.tight_layout()
plt.show()


import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
import lzma
import zlib
from collections import defaultdict

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

# Função para calcular a distância de compressão normalizada (NCD)
def normalized_compression_distance(x, y, compressor):
    # Comprimir x
    x_compressed, _ = compressor(x)
    x_size = len(x_compressed)
    
    # Comprimir y
    y_compressed, _ = compressor(y)
    y_size = len(y_compressed)
    
    # Concatenar e comprimir
    xy = x + y
    xy_compressed, _ = compressor(xy)
    xy_size = len(xy_compressed)
    
    # Calcular NCD
    return (xy_size - min(x_size, y_size)) / max(x_size, y_size)

# Função para processar todos os arquivos de uma região
def process_region_files(region_path, compressor, sample_size=10000):
    files = glob.glob(os.path.join(region_path, "*.txt"))
    if not files:
        print(f"Nenhum arquivo encontrado em {region_path}")
        return None
    
    # Escolha alguns arquivos para representar a região (para ser mais eficiente)
    if len(files) > 10:
        files = files[:10]  # Limitar a 10 arquivos para eficiência
    
    samples = []
    for file in files:
        text = load_text(file)
        # Pegue uma amostra do texto
        sample = text[:sample_size]
        samples.append(sample)
    
    # Concatene todas as amostras em um único texto representativo
    return "".join(samples)

# Função para criar matriz de distância entre regiões
def create_distance_matrix(regions_data, compressor_func, labels):
    n = len(regions_data)
    distance_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            if i == j:
                distance_matrix[i, j] = 0
            else:
                # Calcular a distância de compressão normalizada
                ncd = normalized_compression_distance(regions_data[i], regions_data[j], compressor_func)
                distance_matrix[i, j] = ncd
                distance_matrix[j, i] = ncd  # Matriz simétrica
    
    return distance_matrix

# Função para criar e mostrar o dendrograma
def plot_dendrogram(distance_matrix, labels, title, filename=None):
    # Converter matriz de distância para formato condensado
    condensed_dist = squareform(distance_matrix)
    
    # Calcular o linkage hierárquico
    linkage_matrix = hierarchy.linkage(condensed_dist, method='average')
    
    # Criar figura
    plt.figure(figsize=(10, 6))
    
    # Plotar dendrograma
    hierarchy.dendrogram(
        linkage_matrix,
        labels=labels,
        orientation='top',
        leaf_font_size=12,
        leaf_rotation=90,
    )
    
    plt.title(title, fontsize=14)
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    plt.show()

# Lista de regiões
regions = ['norte', 'nordeste', 'sul', 'sudeste']

# Função principal
def main():
    # Base path para as pastas de dados
    base_path = "db"
    
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
    
    # Média das matrizes para uma comparação combinada
    combined_dist_matrix = (lzma_dist_matrix + lz77_dist_matrix) / 2
    
    # Imprimir matrizes
    print("\nMatriz de Distância LZMA:")
    print_matrix(lzma_dist_matrix, labels)
    
    print("\nMatriz de Distância LZ77:")
    print_matrix(lz77_dist_matrix, labels)
    
    print("\nMatriz de Distância Combinada:")
    print_matrix(combined_dist_matrix, labels)
    
    # Criar dendrogramas
    plot_dendrogram(lzma_dist_matrix, labels, "Dendrograma de Dialetos Regionais (LZMA)", "dendrograma_lzma.png")
    plot_dendrogram(lz77_dist_matrix, labels, "Dendrograma de Dialetos Regionais (LZ77)", "dendrograma_lz77.png")
    plot_dendrogram(combined_dist_matrix, labels, "Dendrograma de Dialetos Regionais (Combinado)", "dendrograma_combinado.png")

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

if __name__ == "__main__":
    main()