import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap
import matplotlib.gridspec as gridspec

def load_regional_data():
    """Carrega os dados de todas as regiões em um único DataFrame."""
    regions = ['nordeste', 'norte', 'sul', 'sudeste']
    
    # Dicionário para armazenar os DataFrames de cada região
    region_dfs = {}
    
    # Carregar dados médios para cada região
    for region in regions:
        try:
            region_path = os.path.join('results', region, 'mean.csv')
            region_df = pd.read_csv(region_path)
            region_dfs[region] = region_df
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {region_path}")
    
    # Carregar dados detalhados para cada região e algoritmo
    all_data = []
    
    for region in regions:
        base_path = os.path.join('results', region)
        
        if not os.path.exists(base_path):
            continue
            
        for algo in ['ppm', 'lzma', 'lz77']:
            # Entropia
            try:
                entropy_file = os.path.join(base_path, f'{algo}_entropy.csv')
                if os.path.exists(entropy_file):
                    df = pd.read_csv(entropy_file)
                    
                    # Verificar a estrutura correta do arquivo
                    print(f"Colunas em {entropy_file}: {df.columns.tolist()}")
                    
                    # Determinar a coluna de entropia correta
                    entropy_col = None
                    if f'{algo.upper()} Entropy' in df.columns:
                        entropy_col = f'{algo.upper()} Entropy'
                    elif algo.upper() == 'PPM' and 'PPM Entropy' in df.columns:
                        entropy_col = 'PPM Entropy'
                    elif algo.upper() == 'LZMA' and 'LZMA Entropy' in df.columns:
                        entropy_col = 'LZMA Entropy'
                    elif algo.upper() == 'LZ77' and 'LZ77 Entropy' in df.columns:
                        entropy_col = 'LZ77 Entropy'
                    
                    if entropy_col:
                        # Criar DataFrame com formato adequado para boxplots
                        text_col = df['Text'] if 'Text' in df.columns else None
                        
                        # Extrair os valores numéricos
                        entropy_values = df[entropy_col]
                        
                        # Criar DataFrame no formato correto
                        new_df = pd.DataFrame({
                            'Value': entropy_values,
                            'Region': region,
                            'Algorithm': algo.upper(),
                            'Metric': 'Entropy'
                        })
                        
                        if text_col is not None:
                            new_df['Text'] = text_col
                        
                        all_data.append(new_df)
                    else:
                        print(f"Coluna de entropia não encontrada em {entropy_file}")
            except Exception as e:
                print(f"Erro ao carregar {entropy_file}: {e}")
                
            # Comprimento médio
            try:
                length_file = os.path.join(base_path, f'{algo}_avg_length.csv')
                if os.path.exists(length_file):
                    df = pd.read_csv(length_file)
                    
                    # Verificar a estrutura correta do arquivo
                    print(f"Colunas em {length_file}: {df.columns.tolist()}")
                    
                    # Determinar a coluna de comprimento médio correta
                    length_col = None
                    if f'{algo.upper()} Avg Length' in df.columns:
                        length_col = f'{algo.upper()} Avg Length'
                    elif algo.upper() == 'PPM' and 'PPM Avg Length' in df.columns:
                        length_col = 'PPM Avg Length'
                    elif algo.upper() == 'LZMA' and 'LZMA Avg Length' in df.columns:
                        length_col = 'LZMA Avg Length'
                    elif algo.upper() == 'LZ77' and 'LZ77 Avg Length' in df.columns:
                        length_col = 'LZ77 Avg Length'
                    
                    if length_col:
                        # Criar DataFrame com formato adequado para boxplots
                        text_col = df['Text'] if 'Text' in df.columns else None
                        
                        # Extrair os valores numéricos
                        length_values = df[length_col]
                        
                        # Criar DataFrame no formato correto
                        new_df = pd.DataFrame({
                            'Value': length_values,
                            'Region': region,
                            'Algorithm': algo.upper(),
                            'Metric': 'Avg Length'
                        })
                        
                        if text_col is not None:
                            new_df['Text'] = text_col
                        
                        all_data.append(new_df)
                    else:
                        print(f"Coluna de comprimento médio não encontrada em {length_file}")
            except Exception as e:
                print(f"Erro ao carregar {length_file}: {e}")
    
    # Combinar todos os dados
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Para depuração
        print("Exemplo do DataFrame combinado:")
        print(combined_df.head())
        
        # Verificar se os dados foram carregados corretamente
        algo_counts = combined_df['Algorithm'].value_counts()
        print("Contagem de registros por algoritmo:")
        print(algo_counts)
        
        region_counts = combined_df['Region'].value_counts()
        print("Contagem de registros por região:")
        print(region_counts)
        
        print(f"Total de registros: {len(combined_df)}")
        print(f"Algoritmos presentes: {combined_df['Algorithm'].unique()}")
        print(f"Regiões presentes: {combined_df['Region'].unique()}")
        print(f"Métricas presentes: {combined_df['Metric'].unique()}")
        return combined_df, region_dfs
    else:
        return None, region_dfs

def load_cross_entropy_data():
    """Carrega a matriz de entropia cruzada."""
    try:
        cross_entropy_file = os.path.join('results', 'static_compression', 'cross_entropy_matrix.csv')
        cross_entropy = pd.read_csv(cross_entropy_file, index_col=0)
        return cross_entropy
    except Exception as e:
        print(f"Erro ao carregar matriz de entropia cruzada: {e}")
        return None

def load_kl_divergence_data():
    """Carrega a matriz de divergência KL."""
    try:
        kl_file = os.path.join('results', 'static_compression', 'kl_divergence_matrix.csv')
        kl_divergence = pd.read_csv(kl_file, index_col=0)
        return kl_divergence
    except Exception as e:
        print(f"Erro ao carregar matriz de divergência KL: {e}")
        return None

def plot_boxplots(data):
    """Gera boxplots para entropia e comprimento médio por região e algoritmo."""
    if data is None:
        print("Sem dados para plotar boxplots.")
        return
    
    # Verificar quais colunas existem nos dados
    print("Colunas disponíveis:", data.columns.tolist())
    
    # Configuração visual
    sns.set(style="whitegrid")
    plt.figure(figsize=(15, 10))
    
    # Plot de Entropia por Região e Algoritmo
    plt.subplot(2, 1, 1)
    entropy_data = data[data['Metric'] == 'Entropy']
    
    if 'Value' in entropy_data.columns:
        # Converter coluna para numérico
        entropy_data['Value'] = pd.to_numeric(entropy_data['Value'], errors='coerce')
        
        sns.boxplot(x='Region', y='Value', hue='Algorithm', data=entropy_data)
        plt.title('Entropia por Região e Algoritmo', fontsize=16)
        plt.xlabel('Região', fontsize=14)
        plt.ylabel('Entropia', fontsize=14)
        plt.legend(title='Algoritmo')
    else:
        print("Coluna 'Value' não encontrada nos dados de entropia")
    
    # Plot de Comprimento Médio por Região e Algoritmo
    plt.subplot(2, 1, 2)
    length_data = data[data['Metric'] == 'Avg Length']
    
    if 'Value' in length_data.columns:
        # Converter coluna para numérico
        length_data['Value'] = pd.to_numeric(length_data['Value'], errors='coerce')
        
        sns.boxplot(x='Region', y='Value', hue='Algorithm', data=length_data)
        plt.title('Comprimento Médio por Região e Algoritmo', fontsize=16)
        plt.xlabel('Região', fontsize=14)
        plt.ylabel('Comprimento Médio', fontsize=14)
        plt.legend(title='Algoritmo')
    else:
        print("Coluna 'Value' não encontrada nos dados de comprimento médio")
    
    plt.tight_layout()
    plt.savefig('boxplots_comparacao_regioes.png', dpi=300)
    plt.close()
    
    print("Boxplots gerados: boxplots_comparacao_regioes.png")

def plot_means_table(region_dfs):
    """Cria uma tabela com as médias de entropia para cada região."""
    if not region_dfs:
        print("Sem dados para criar tabela de médias.")
        return
    
    # Preparar dados para a tabela
    table_data = []
    for region, df in region_dfs.items():
        if not df.empty:
            row = {
                'Região': region.capitalize(),
                'PPM Entropia': df['PPM Entropy'].iloc[0] if 'PPM Entropy' in df.columns else np.nan,
                'LZMA Entropia': df['LZMA Entropy'].iloc[0] if 'LZMA Entropy' in df.columns else np.nan,
                'LZ77 Entropia': df['LZ77 Entropy'].iloc[0] if 'LZ77 Entropy' in df.columns else np.nan
            }
            table_data.append(row)
    
    if table_data:
        means_df = pd.DataFrame(table_data)
        
        # Criar uma figura para a tabela
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.axis('tight')
        ax.axis('off')
        
        # Criar tabela
        table = ax.table(
            cellText=means_df.round(4).values,
            colLabels=means_df.columns,
            cellLoc='center',
            loc='center',
            colColours=['#f2f2f2']*len(means_df.columns)
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        plt.title('Médias de Entropia por Região', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('tabela_medias_regioes.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Tabela de médias gerada: tabela_medias_regioes.png")
        
        # Salvar em CSV também
        means_df.to_csv('tabela_medias_regioes.csv', index=False)
        print("Tabela de médias salva em CSV: tabela_medias_regioes.csv")

def plot_cross_entropy_heatmap(cross_entropy_data):
    """Plota um heatmap da matriz de entropia cruzada."""
    if cross_entropy_data is None:
        print("Sem dados para plotar heatmap de entropia cruzada.")
        return
    
    plt.figure(figsize=(10, 8))
    
    # Criar uma paleta de cores personalizada
    cmap = sns.color_palette("YlOrRd", as_cmap=True)
    
    # Plotar o heatmap
    ax = sns.heatmap(
        cross_entropy_data, 
        annot=True, 
        fmt=".4f", 
        cmap=cmap,
        linewidths=.5, 
        cbar_kws={'label': 'Entropia Cruzada'}
    )
    
    plt.title('Matriz de Entropia Cruzada Entre Regiões', fontsize=16)
    plt.xlabel('Modelo Destino', fontsize=14)
    plt.ylabel('Texto de Origem', fontsize=14)
    
    # Ajuste para visualização melhor
    plt.tight_layout()
    plt.savefig('heatmap_entropia_cruzada.png', dpi=300)
    plt.close()
    
    print("Heatmap de entropia cruzada gerado: heatmap_entropia_cruzada.png")

def plot_kl_divergence_heatmap(kl_data):
    """Plota um heatmap da matriz de divergência KL."""
    if kl_data is None:
        print("Sem dados para plotar heatmap de divergência KL.")
        return
    
    plt.figure(figsize=(10, 8))
    
    # Criar uma paleta de cores personalizada
    cmap = sns.color_palette("YlGnBu", as_cmap=True)
    
    # Plotar o heatmap
    ax = sns.heatmap(
        kl_data, 
        annot=True, 
        fmt=".4f", 
        cmap=cmap,
        linewidths=.5, 
        cbar_kws={'label': 'Divergência KL'}
    )
    
    plt.title('Matriz de Divergência KL Entre Regiões', fontsize=16)
    plt.xlabel('Modelo Destino', fontsize=14)
    plt.ylabel('Texto de Origem', fontsize=14)
    
    # Ajuste para visualização melhor
    plt.tight_layout()
    plt.savefig('heatmap_divergencia_kl.png', dpi=300)
    plt.close()
    
    print("Heatmap de divergência KL gerado: heatmap_divergencia_kl.png")

def plot_boxplots_by_algorithm(data):
    """Gera boxplots separados para cada algoritmo, comparando as regiões."""
    if data is None:
        print("Sem dados para plotar boxplots por algoritmo.")
        return
    
    # Configuração visual
    sns.set(style="whitegrid")
    
    # Criar subplots para cada algoritmo e tipo de métrica
    plt.figure(figsize=(20, 16))
    
    # Dados de entropia
    entropy_data = data[data['Metric'] == 'Entropy']
    entropy_data['Value'] = pd.to_numeric(entropy_data['Value'], errors='coerce')
    
    # Dados de comprimento médio
    length_data = data[data['Metric'] == 'Avg Length']
    length_data['Value'] = pd.to_numeric(length_data['Value'], errors='coerce')
    
    # Lista de algoritmos disponíveis
    algorithms = sorted(data['Algorithm'].unique())
    
    # Configurar grid de subplots
    grid = gridspec.GridSpec(2, len(algorithms))
    
    # Cores para cada região
    region_colors = {
        'nordeste': '#1f77b4',  # azul
        'norte': '#ff7f0e',     # laranja
        'sul': '#2ca02c',       # verde
        'sudeste': '#d62728'    # vermelho
    }
    
    # Plotar entropia para cada algoritmo
    for i, algo in enumerate(algorithms):
        ax = plt.subplot(grid[0, i])
        
        # Filtrar dados para o algoritmo atual
        algo_entropy = entropy_data[entropy_data['Algorithm'] == algo]
        
        # Boxplot para o algoritmo
        sns.boxplot(x='Region', y='Value', data=algo_entropy, ax=ax, 
                    palette=[region_colors.get(r, 'gray') for r in sorted(algo_entropy['Region'].unique())])
        
        ax.set_title(f'Entropia - {algo}', fontsize=14)
        ax.set_xlabel('Região', fontsize=12)
        ax.set_ylabel('Entropia', fontsize=12)
        
        # Ajustar os ticks do eixo x
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adicionar média como uma linha pontilhada para cada região
        for region in sorted(algo_entropy['Region'].unique()):
            region_data = algo_entropy[algo_entropy['Region'] == region]
            mean_val = region_data['Value'].mean()
            ax.axhline(y=mean_val, color=region_colors.get(region, 'gray'), 
                       linestyle='--', linewidth=1.5, alpha=0.7)
    
    # Plotar comprimento médio para cada algoritmo
    for i, algo in enumerate(algorithms):
        ax = plt.subplot(grid[1, i])
        
        # Filtrar dados para o algoritmo atual
        algo_length = length_data[length_data['Algorithm'] == algo]
        
        # Boxplot para o algoritmo
        sns.boxplot(x='Region', y='Value', data=algo_length, ax=ax,
                    palette=[region_colors.get(r, 'gray') for r in sorted(algo_length['Region'].unique())])
        
        ax.set_title(f'Comprimento Médio - {algo}', fontsize=14)
        ax.set_xlabel('Região', fontsize=12)
        ax.set_ylabel('Comprimento Médio', fontsize=12)
        
        # Ajustar os ticks do eixo x
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adicionar média como uma linha pontilhada para cada região
        for region in sorted(algo_length['Region'].unique()):
            region_data = algo_length[algo_length['Region'] == region]
            mean_val = region_data['Value'].mean()
            ax.axhline(y=mean_val, color=region_colors.get(region, 'gray'), 
                       linestyle='--', linewidth=1.5, alpha=0.7)
    
    # Configurar o título principal e ajustes finais
    plt.suptitle('Comparação por Algoritmo de Compressão', fontsize=18)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    # Salvar a figura
    plt.savefig('boxplots_por_algoritmo.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Boxplots por algoritmo gerados: boxplots_por_algoritmo.png")

def plot_summary_dashboard():
    """Plota um dashboard resumido com todos os gráficos e tabelas."""
    # Carregar todos os dados
    data, region_dfs = load_regional_data()
    cross_entropy_data = load_cross_entropy_data()
    kl_data = load_kl_divergence_data()
    
    # Configuração da figura principal
    plt.figure(figsize=(20, 16))
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1], height_ratios=[1, 1])
    
    # 1. Boxplot de Entropia
    ax1 = plt.subplot(gs[0, 0])
    if data is not None:
        entropy_data = data[data['Metric'] == 'Entropy']
        
        if 'Value' in entropy_data.columns:
            entropy_data['Value'] = pd.to_numeric(entropy_data['Value'], errors='coerce')
            
            sns.boxplot(x='Region', y='Value', hue='Algorithm', data=entropy_data, ax=ax1)
            ax1.set_title('Entropia por Região', fontsize=14)
            ax1.set_xlabel('Região', fontsize=12)
            ax1.set_ylabel('Entropia', fontsize=12)
            ax1.legend(title='Algoritmo', fontsize=10)
    
    # 2. Heatmap de Entropia Cruzada
    ax2 = plt.subplot(gs[0, 1])
    if cross_entropy_data is not None:
        cmap = sns.color_palette("YlOrRd", as_cmap=True)
        sns.heatmap(
            cross_entropy_data, 
            annot=True, 
            fmt=".4f", 
            cmap=cmap,
            linewidths=.5, 
            cbar_kws={'label': 'Entropia Cruzada'},
            ax=ax2
        )
        ax2.set_title('Entropia Cruzada Entre Regiões', fontsize=14)
        ax2.set_xlabel('Modelo Destino', fontsize=12)
        ax2.set_ylabel('Texto de Origem', fontsize=12)
    
    # 3. Boxplot de Comprimento Médio
    ax3 = plt.subplot(gs[1, 0])
    if data is not None:
        length_data = data[data['Metric'] == 'Avg Length']
        
        if 'Value' in length_data.columns:
            length_data['Value'] = pd.to_numeric(length_data['Value'], errors='coerce')
            
            sns.boxplot(x='Region', y='Value', hue='Algorithm', data=length_data, ax=ax3)
            ax3.set_title('Comprimento Médio por Região', fontsize=14)
            ax3.set_xlabel('Região', fontsize=12)
            ax3.set_ylabel('Comprimento Médio', fontsize=12)
            ax3.legend(title='Algoritmo', fontsize=10)
    
    # 4. Heatmap de Divergência KL
    ax4 = plt.subplot(gs[1, 1])
    if kl_data is not None:
        cmap = sns.color_palette("YlGnBu", as_cmap=True)
        sns.heatmap(
            kl_data, 
            annot=True, 
            fmt=".4f", 
            cmap=cmap,
            linewidths=.5, 
            cbar_kws={'label': 'Divergência KL'},
            ax=ax4
        )
        ax4.set_title('Divergência KL Entre Regiões', fontsize=14)
        ax4.set_xlabel('Modelo Destino', fontsize=12)
        ax4.set_ylabel('Texto de Origem', fontsize=12)
    
    # Ajustes finais
    plt.suptitle('Dashboard de Análise de Classificadores Regionais', fontsize=20)
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    # Salvar figura
    plt.savefig('dashboard_analise_regional.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Dashboard de análise regional gerado: dashboard_analise_regional.png")

if __name__ == "__main__":
    print("Gerando gráficos e tabelas para apresentação...")
    
    # Carregar dados
    data, region_dfs = load_regional_data()
    cross_entropy_data = load_cross_entropy_data()
    kl_data = load_kl_divergence_data()
    
    # Gerar visualizações individuais
    plot_boxplots(data)
    plot_means_table(region_dfs)
    plot_cross_entropy_heatmap(cross_entropy_data)
    plot_kl_divergence_heatmap(kl_data)
    
    # Gerar boxplots por algoritmo
    plot_boxplots_by_algorithm(data)
    
    # Gerar dashboard resumido
    plot_summary_dashboard()
    
    print("Todos os gráficos e tabelas foram gerados com sucesso!") 