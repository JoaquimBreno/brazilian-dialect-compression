#!/bin/bash

# Script para contar caracteres e palavras por região
# Autor: Claude

# Verifica se o gnuplot está instalado
if ! command -v gnuplot &> /dev/null; then
    echo "Gnuplot não está instalado. Por favor, instale-o com 'brew install gnuplot' ou equivalente."
    exit 1
fi

# Cores para melhor visualização
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Contabilizando caracteres e palavras por região...${NC}\n"

# Array com as regiões
regions=("norte" "nordeste" "sudeste" "sul")

# Contagem total
total_chars=0
total_words=0

# Arquivo de dados para o gnuplot
data_file="region_stats.dat"
echo "# Região Caracteres Palavras" > $data_file

# Loop por região
for region in "${regions[@]}"; do
    # Verifica se o diretório de textos existe
    if [ -d "db/${region}/texts" ]; then
        # Inicializa contadores para a região
        region_chars=0
        region_words=0
        
        # Loop por todos os arquivos .txt na pasta de textos
        for file in db/${region}/texts/*_clean.txt; do
            if [ -f "$file" ]; then
                # Conta caracteres no arquivo
                file_chars=$(wc -c < "$file")
                region_chars=$((region_chars + file_chars))
                
                # Conta palavras no arquivo (considerando palavras separadas por '_' no texto limpo)
                # Substitui '_' por espaços para contar palavras corretamente
                file_content=$(cat "$file" | tr '_' ' ')
                file_words=$(echo "$file_content" | wc -w)
                region_words=$((region_words + file_words))
            fi
        done
        
        # Formata os números com separadores de milhares
        formatted_chars=$(echo $region_chars | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta')
        formatted_words=$(echo $region_words | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta')
        
        # Imprime resultado da região
        echo -e "${BLUE}Região ${region^}:${NC}"
        echo -e "  Caracteres: $formatted_chars"
        echo -e "  Palavras: $formatted_words\n"
        
        # Adiciona ao total
        total_chars=$((total_chars + region_chars))
        total_words=$((total_words + region_words))
        
        # Adiciona ao arquivo de dados
        echo "${region} $region_chars $region_words" >> $data_file
    else
        echo "Diretório db/${region}/texts não encontrado"
    fi
done

# Formata os números totais com separadores de milhares
formatted_total_chars=$(echo $total_chars | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta')
formatted_total_words=$(echo $total_words | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta')

# Imprime o total geral
echo -e "${GREEN}Totais gerais:${NC}"
echo -e "  Caracteres: $formatted_total_chars"
echo -e "  Palavras: $formatted_total_words"

# Criando o script para o gnuplot
gnuplot_script="plot_regions.gp"
cat > $gnuplot_script << EOF
set terminal png size 800,600 enhanced font 'Verdana,10'
set output 'regiao_stats.png'
set title 'Estatísticas por Região' font 'Verdana,14'
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9
set xtic scale 0
set ylabel "Quantidade"
set yrange [0:*]
set grid y
set key outside
set datafile separator whitespace

# Define paleta de cores mais atraente
set palette defined (0 "#4575b4", 1 "#91bfdb", 2 "#e0f3f8", 3 "#ffffbf", 4 "#fee090", 5 "#fc8d59", 6 "#d73027")
set cbrange [0:6]
unset colorbox

# Formata o eixo Y com separadores de milhares
set format y "%'.0f"

# Plota dados normalizados para melhor visualização
plot "$data_file" using 2:xtic(1) title "Caracteres" linecolor rgb "#4575b4", \
     "" using 3 title "Palavras" linecolor rgb "#d73027"
EOF

# Executando o gnuplot
echo -e "\n${GREEN}Gerando gráfico...${NC}"
gnuplot $gnuplot_script

# Verificando se o gráfico foi gerado com sucesso
if [ -f "regiao_stats.png" ]; then
    echo -e "${GREEN}Gráfico gerado com sucesso:${NC} regiao_stats.png"
    
    # Tenta abrir o gráfico com o visualizador padrão do sistema
    if [ "$(uname)" == "Darwin" ]; then  # macOS
        open regiao_stats.png
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        xdg-open regiao_stats.png &> /dev/null || echo "Não foi possível abrir automaticamente. Abra o arquivo regiao_stats.png manualmente."
    fi
else
    echo -e "${RED}Falha ao gerar o gráfico.${NC}"
fi 