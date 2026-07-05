# Hash Linear

Este repositório contém a implementação em Python, a avaliação de desempenho empírico e uma interface gráfica interativa para o algoritmo de **Hash Linear** de W. Litwin. 

O projeto foi desenvolvido como trabalho prático da disciplina de Estrutura de Dados 2 do curso de Ciência da Computação da Universidade Federal da Bahia (UFBA).

## 📌 Escopo do Projeto

O projeto é estruturado em duas vertentes principais (Acadêmica e Didática):

1. **Avaliação Experimental (Obrigatória):** Implementação da estrutura de dados simulando partições em disco e execução de uma bateria massiva de testes (100.000 inserções dinâmicas e 10.000 buscas). O objetivo é comprovar o *trade-off* entre o tempo de busca e a fragmentação (páginas de transbordamento) ao variar a capacidade da página (`P`) e o limite do fator de carga (`α_max`).
2. **🌟 Visualizador Web (Adicional Frontend):** Para facilitar o entendimento didático da mecânica do algoritmo, o repositório conta com uma implementação extra. Trata-se de uma aplicação Web (*Full-Stack*) que renderiza visualmente a criação, o limite de ocupação e o encadeamento de *overflow* dos *buckets* da tabela em tempo real a cada inserção.

## 📂 Estrutura do Repositório

* `linear_hash.py`: Motor principal contendo a classe do Hash Linear e a automação do experimento de desempenho (gera os gráficos analíticos usando `matplotlib`).
* `app.py`: *Backend* em Flask (Implementação Extra) que provê uma API com o estado interno do algoritmo.
* `templates/index.html`: *Frontend* (Implementação Extra) que consome o *backend* para renderizar de forma interativa a estrutura de dados na tela.
* `graficos/`: Diretório de saída contendo as evidências visuais da degradação de desempenho e do uso de memória extraídas da bateria de testes.

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de ter o Python 3.8+ instalado em sua máquina. Para instalar as dependências do projeto, execute o comando abaixo no seu terminal:
```bash
pip install flask matplotlib

1. Rodar os Experimentos 

Para reproduzir os testes de carga pesada descritos no artigo científico e gerar as métricas de tempo de busca e uso de espaço:
Bash

python linear_hash.py

2. Rodar a Interface gráfica

Para abrir a interface gráficae entender o funcionamento passo a passoo:
Bash

python app.py

Em seguida, acesse http://127.0.0.1:5000 em seu navegador.
