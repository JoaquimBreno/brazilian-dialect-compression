import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform

# Dados das matrizes de distância do resultado
# Matriz LZMA
lzma_matrix = np.array([
    [0.000000, 0.942943, 0.938800, 0.943874],
    [0.942943, 0.000000, 0.943180, 0.945375],
    [0.938800, 0.943180, 0.000000, 0.941443],
    [0.943874, 0.945375, 0.941443, 0.000000]
])

# Matriz LZ77
lz77_matrix = np.array([
    [0.000000, 0.994758, 0.993799, 0.994514],
    [0.994758, 0.000000, 0.993654, 0.993363],
    [0.993799, 0.993654, 0.000000, 0.993690],
    [0.994514, 0.993363, 0.993690, 0.000000]
])

# Matriz PPM
ppm_matrix = np.array([
    [0.000000, 0.994313, 0.991570, 0.992980],
    [0.994313, 0.000000, 0.991603, 0.992122],
    [0.991570, 0.991603, 0.000000, 0.991156],
    [0.992980, 0.992122, 0.991156, 0.000000]
])

# Matriz Combinada
combined_matrix = np.array([
    [0.000000, 0.977338, 0.974723, 0.977123],
    [0.977338, 0.000000, 0.976146, 0.976954],
    [0.974723, 0.976146, 0.000000, 0.975430],
    [0.977123, 0.976954, 0.975430, 0.000000]
])

# Rótulos das regiões
labels = ['Norte', 'Nordeste', 'Sul', 'Sudeste']

# Função para normalizar as matrizes para uma escala mais adequada
def normalize_matrix(matrix):
    # Encontra os valores mínimo e máximo (excluindo zeros da diagonal)
    non_zero = matrix[matrix > 0]
    min_val = non_zero.min()
    max_val = non_zero.max()
    
    # Normalização para ampliar as diferenças
    normalized = np.zeros_like(matrix)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if i != j:  # Mantém zeros na diagonal
                # Amplifica diferenças - mapeia para escala [0, 1]
                normalized[i, j] = (matrix[i, j] - min_val) / (max_val - min_val)
    
    return normalized

# Função para criar e mostrar o dendrograma com uma escala melhor
def plot_enhanced_dendrogram(distance_matrix, labels, title, filename=None):
    # Normalizar a matriz para ampliar diferenças
    norm_matrix = normalize_matrix(distance_matrix)
    
    # Converter matriz de distância para formato condensado
    condensed_dist = squareform(norm_matrix)
    
    # Calcular o linkage hierárquico
    linkage_matrix = hierarchy.linkage(condensed_dist, method='average')
    
    # Criar figura
    plt.figure(figsize=(10, 6))
    
    # Plotar dendrograma
    dendrogram = hierarchy.dendrogram(
        linkage_matrix,
        labels=labels,
        orientation='top',
        leaf_font_size=12,
        leaf_rotation=90,
        color_threshold=0.3  # Ajusta para destacar clusters
    )
    
    # Adicionar linhas horizontais para facilitar interpretação
    for i in np.arange(0.1, 1.1, 0.1):
        plt.axhline(y=i, color='gray', linestyle='--', alpha=0.3)
    
    plt.title(title, fontsize=16)
    plt.ylabel('Distância Normalizada', fontsize=12)
    plt.ylim(0, 1.1)  # Limita o eixo Y a [0, 1.1]
    
    # Adicionar anotações mostrando os valores originais
    if filename:
        plt.text(0.02, 0.98, f"Amplitude original: {distance_matrix[distance_matrix > 0].min():.6f} - {distance_matrix.max():.6f}", 
                 transform=plt.gca().transAxes, fontsize=9, verticalalignment='top')
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    plt.show()

# Criar e mostrar dendrogramas melhorados para cada matriz
plot_enhanced_dendrogram(lzma_matrix, labels, 
                        "Dendrograma de Dialetos Regionais (LZMA)", 
                        "dendrograma_lzma_enhanced.png")

plot_enhanced_dendrogram(lz77_matrix, labels, 
                        "Dendrograma de Dialetos Regionais (LZ77)", 
                        "dendrograma_lz77_enhanced.png")

plot_enhanced_dendrogram(ppm_matrix, labels, 
                        "Dendrograma de Dialetos Regionais (PPM)", 
                        "dendrograma_ppm_enhanced.png")

plot_enhanced_dendrogram(combined_matrix, labels, 
                        "Dendrograma de Dialetos Regionais (Combinado)", 
                        "dendrograma_combinado_enhanced.png")

# Versão comparativa em uma única figura
plt.figure(figsize=(15, 10))

# Criar subplots para cada compressor
plt.subplot(2, 2, 1)
condensed_dist = squareform(normalize_matrix(lzma_matrix))
linkage_matrix = hierarchy.linkage(condensed_dist, method='average')
hierarchy.dendrogram(linkage_matrix, labels=labels, leaf_font_size=10, leaf_rotation=90)
plt.title("LZMA", fontsize=14)
plt.ylim(0, 1.1)

plt.subplot(2, 2, 2)
condensed_dist = squareform(normalize_matrix(lz77_matrix))
linkage_matrix = hierarchy.linkage(condensed_dist, method='average')
hierarchy.dendrogram(linkage_matrix, labels=labels, leaf_font_size=10, leaf_rotation=90)
plt.title("LZ77", fontsize=14)
plt.ylim(0, 1.1)

plt.subplot(2, 2, 3)
condensed_dist = squareform(normalize_matrix(ppm_matrix))
linkage_matrix = hierarchy.linkage(condensed_dist, method='average')
hierarchy.dendrogram(linkage_matrix, labels=labels, leaf_font_size=10, leaf_rotation=90)
plt.title("PPM", fontsize=14)
plt.ylim(0, 1.1)

plt.subplot(2, 2, 4)
condensed_dist = squareform(normalize_matrix(combined_matrix))
linkage_matrix = hierarchy.linkage(condensed_dist, method='average')
hierarchy.dendrogram(linkage_matrix, labels=labels, leaf_font_size=10, leaf_rotation=90)
plt.title("Combinado", fontsize=14)
plt.ylim(0, 1.1)

plt.suptitle("Comparação de Dendrogramas por Método de Compressão", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("dendrograma_comparativo.png", dpi=300, bbox_inches='tight')
plt.show()

# Plotar também as matrizes originais como heatmaps para comparação
def plot_heatmap(matrix, title, filename=None):
    plt.figure(figsize=(8, 6))
    plt.imshow(matrix, cmap='viridis')
    
    # Adicionar valores nas células
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            text_color = 'white' if matrix[i, j] > 0.5 else 'black'
            plt.text(j, i, f"{matrix[i, j]:.4f}", ha="center", va="center", color=text_color)
    
    plt.colorbar(label='Distância')
    plt.xticks(np.arange(len(labels)), labels)
    plt.yticks(np.arange(len(labels)), labels)
    plt.title(title)
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    plt.tight_layout()
    plt.show()

# Criar heatmaps para visualizar as matrizes de distância
plot_heatmap(lzma_matrix, "Matriz de Distância LZMA", "heatmap_lzma.png")
plot_heatmap(lz77_matrix, "Matriz de Distância LZ77", "heatmap_lz77.png")
plot_heatmap(ppm_matrix, "Matriz de Distância PPM", "heatmap_ppm.png")
plot_heatmap(combined_matrix, "Matriz de Distância Combinada", "heatmap_combinado.png") 