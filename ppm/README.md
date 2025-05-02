# PPM - Prediction by Partial Matching

Este projeto implementa um modelo PPM (Prediction by Partial Matching) para compressão e análise de texto.

## Como executar?

Da pasta exterior a ppm:

```bash
python main.py
```

## Estrutura do Projeto

```
ppm/
├── main.py             # Ponto de entrada principal que configura e executa a aplicação
├── app.py              # Define a classe PPMApp que coordena o processamento
├── models/             # Contém as definições do modelo PPM e estruturas de dados auxiliares
│   ├── context.py      # Implementa a classe Context para gerenciar contextos no PPM
│   └── ppm_model.py    # Implementa o modelo PPM principal
├── processors/         # Contém processadores para o modelo
│   └── ppm_processor.py # Implementa o processador PPM para tratar sequências de texto
└── utils/              # Utilitários para o projeto
    └── file_handler.py # Manipula operações de arquivos
```

## Funcionamento

O algoritmo PPM (Prediction by Partial Matching) é um método de compressão de dados que utiliza um modelo de contexto para prever símbolos em uma sequência. Este projeto implementa:

1. Um sistema de contextos de tamanho variável (k = -1 até k_max)
2. Processamento de caracteres com símbolos de escape para contextos não encontrados
3. Estrutura modular para facilitar extensões e modificações

Os principais componentes incluem:
- `PPMApp`: Coordena a aplicação, gerenciando o processamento do texto e o modelo
- `PPMModel`: Implementa o modelo estatístico e a estrutura de dados do PPM
- `PPMProcessor`: Gerencia o processamento do texto usando o modelo
- `Context`: Representa um contexto específico no modelo, armazenando contagens de caracteres

## Configuração

Você pode ajustar parâmetros como o valor de K_MAX e o arquivo de entrada no arquivo `main.py`.
