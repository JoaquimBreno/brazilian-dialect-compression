# Database Processing Scripts

Este diretório contém scripts para processamento de e-books por região (Nordeste, Norte, Sul, etc.). Os scripts devem ser executados dentro da pasta específica de cada região.

## Estrutura de Diretórios

A estrutura de diretórios do banco de dados é organizada da seguinte forma:

```
db/
├── README.md
├── convert_all.sh
├── pdf_to_clean_text.py
├── nordeste/
│   ├── [arquivos .epub, .mobi, .azw3, .pdf]
│   ├── texts/
│   │   └── [arquivos _clean.txt]
│   └── splits/
│       ├── train/
│       ├── test/
│       └── valid/
├── norte/
│   ├── [...]
├── sul/
│   ├── [...]
├── sudeste/
│   ├── [...]
└── centro_oeste/
    └── [...]
```

* `db/` - Diretório principal contendo os scripts e pastas regionais
* `[região]/` - Pastas específicas para cada região (nordeste, norte, sul, sudeste, centro_oeste)
* `texts/` - Pasta gerada pelo script que contém os textos extraídos e normalizados
* `splits/` - Pasta contendo as divisões de dados para treinamento, teste e validação

## Scripts Disponíveis

### 1. `convert_all.sh`

Script para converter e-books de vários formatos para PDF.

**Funcionalidade:**

- Converte arquivos nos formatos EPUB, MOBI e AZW3 para PDF
- Remove automaticamente os arquivos originais após conversão bem-sucedida
- Exibe mensagens de status para cada conversão

**Uso:**

```bash
cd [pasta_da_região]  # Ex: cd nordeste
bash ../db/convert_all.sh
```

**Requisitos:**

- Calibre instalado (para o comando `ebook-convert`)

### 2. `pdf_to_clean_text.py`

Script Python que processa arquivos PDF e os converte em texto normalizado para treinamento de modelos.

**Funcionalidade:**

- Extrai texto de todos os PDFs em um diretório
- Normaliza o texto (remove acentos, converte para minúsculas, substitui espaços por underscores)
- Cria uma pasta `texts` com os textos extraídos e normalizados
- Divide os textos em lotes (batches) para treinamento, teste e validação
- Cria uma estrutura de diretórios `splits/train`, `splits/test` e `splits/valid`

**Uso:**

```bash
cd [pasta_da_região]  # Ex: cd nordeste
python ../db/pdf_to_clean_text.py ./
```

**Resultado:**

- Gera arquivos de texto limpos em `[pasta_da_região]/texts/`
- Cria splits para treinamento em `[pasta_da_região]/splits/train/`, `[pasta_da_região]/splits/test/` e `[pasta_da_região]/splits/valid/`

**Requisitos:**

- Python 3.x
- Biblioteca PyPDF2 (`pip install PyPDF2`)

## Fluxo de Processamento Recomendado

1. Coloque os e-books (EPUB, MOBI, AZW3) na pasta da região específica
2. Execute `convert_all.sh` para converter tudo para PDF
3. Execute `ebook_manager.py` para limpar o pdf (remover capas e sumarios)
4. Execute `pdf_to_clean_text.py` para extrair e normalizar o texto
5. Utilize os arquivos gerados em `splits/` para treinamento do classificador regional
