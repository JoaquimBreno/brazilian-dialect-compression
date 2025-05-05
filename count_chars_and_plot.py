#!/usr/bin/env python3

import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

def format_number(num):
    """Formata número com separadores de milhares."""
    return f"{num:,}"

def main():
    print("Contabilizando caracteres e palavras por região...\n")
    
    # Array com as regiões
    regions = ["norte", "nordeste", "sudeste", "sul"]
    
    # Dicionários para armazenar resultados
    chars_by_region = OrderedDict()
    words_by_region = OrderedDict()
    
    # Contagem total
    total_chars = 0
    total_words = 0
    
    # Loop por região
    for region in regions:
        texts_dir = os.path.join("db", region, "texts")
        
        # Verifica se o diretório de textos existe
        if os.path.isdir(texts_dir):
            # Inicializa contadores para a região
            region_chars = 0
            region_words = 0
            
            # Loop por todos os arquivos .txt na pasta de textos
            for filename in os.listdir(texts_dir):
                if filename.endswith("_clean.txt"):
                    file_path = os.path.join(texts_dir, filename)
                    
                    # Lê o conteúdo do arquivo
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        
                        # Conta caracteres
                        file_chars = len(content)
                        region_chars += file_chars
                        
                        # Conta palavras (substituindo underscores por espaços)
                        content_with_spaces = content.replace('_', ' ')
                        file_words = len(content_with_spaces.split())
                        region_words += file_words
            
            # Armazena resultados no dicionário
            chars_by_region[region] = region_chars
            words_by_region[region] = region_words
            
            # Imprime resultado da região
            print(f"Região {region.capitalize()}:")
            print(f"  Caracteres: {format_number(region_chars)}")
            print(f"  Palavras: {format_number(region_words)}\n")
            
            # Adiciona ao total
            total_chars += region_chars
            total_words += region_words
        else:
            print(f"Diretório db/{region}/texts não encontrado")
    
    # Imprime o total geral
    print(f"Totais gerais:")
    print(f"  Caracteres: {format_number(total_chars)}")
    print(f"  Palavras: {format_number(total_words)}")
    
    # Verifica se temos dados para plotar
    if not chars_by_region:
        print("Nenhum dado para plotar!")
        return
    
    # Preparando dados para o gráfico
    region_names = list(chars_by_region.keys())
    char_values = list(chars_by_region.values())
    word_values = list(words_by_region.values())
    
    # Configurando o gráfico
    plt.figure(figsize=(10, 6))
    
    # Posição das barras
    x = np.arange(len(region_names))
    width = 0.35
    
    # Criando as barras
    plt.bar(x - width/2, char_values, width, label='Caracteres', color='#4575b4')
    plt.bar(x + width/2, word_values, width, label='Palavras', color='#d73027')
    
    # Adicionando rótulos e título
    plt.title('Estatísticas por Região', fontsize=14)
    plt.xlabel('Região')
    plt.ylabel('Quantidade')
    plt.xticks(x, [region.capitalize() for region in region_names])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # Adicionando valores numéricos nas barras
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.05 * max(char_values),
                    f'{format_number(int(height))}',
                    ha='center', va='bottom', rotation=0, fontsize=8)
            
    # Adiciona rótulos
    bars1 = plt.bar(x - width/2, char_values, width)
    bars2 = plt.bar(x + width/2, word_values, width)
    add_labels(bars1)
    add_labels(bars2)
    
    # Ajuste automático de layout
    plt.tight_layout()
    
    # Salvando o gráfico
    plt.savefig('regiao_stats.png', dpi=300)
    print("\nGráfico gerado com sucesso: regiao_stats.png")
    
    # Mostrando o gráfico (opcional, pode ser comentado se não quiser exibir)
    plt.show()

if __name__ == "__main__":
    main() 