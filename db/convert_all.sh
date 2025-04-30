#!/bin/bash

echo "=== Convertendo todos os e-books para PDF e removendo originais ==="
echo

# Função para converter e remover
convert_and_remove() {
    local file="$1"
    local pdf_file="${file%.*}.pdf"
    echo "Convertendo $file..."
    if ebook-convert "$file" "$pdf_file" && [ -f "$pdf_file" ]; then
        echo "Conversão bem-sucedida. Removendo arquivo original..."
        rm "$file"
        echo "✓ $file removido"
    else
        echo "❌ Erro na conversão de $file - arquivo original mantido"
    fi
    echo "---"
}

# Converter e remover arquivos EPUB
for file in *.epub; do
    if [ -f "$file" ]; then
        convert_and_remove "$file"
    fi
done

# Converter e remover arquivos MOBI
for file in *.mobi; do
    if [ -f "$file" ]; then
        convert_and_remove "$file"
    fi
done

# Converter e remover arquivos AZW3
for file in *.azw3; do
    if [ -f "$file" ]; then
        convert_and_remove "$file"
    fi
done

echo "Processo concluído!"
echo "Arquivos convertidos para PDF e originais removidos." 