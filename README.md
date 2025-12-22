# GRUPO 6
 - PG11605 - Carlos da Mota Bergueira 
 - PG59999 - Diego Jefferson Mendes Silva 
 - PG42201 - Filipa Araújo Pereira
 - PG7942  - Rui Manuel Martins Marques Rodrigues


# 🚀 Resumo do Projeto
Este repositório contém um motor de roteamento multimodal de última geração, focado na Área Metropolitana do Porto. O sistema integra dados reais de transportes (Metro do Porto e STCP) com a malha urbana do OpenStreetMap, permitindo calcular trajetos que equilibram não só o tempo, mas também a sustentabilidade e a saúde.

## ✨ Destaques

* Otimização Multi-Objetivo: Encontra o equilíbrio ideal entre Tempo de Viagem, Emissões de CO2 e Exercício Físico (distância a pé).
* Fronteira de Pareto: O utilizador não recebe apenas uma rota, mas sim um conjunto de opções ótimas (as melhores em cada categoria).
* Integração Geográfica Real: Utiliza a biblioteca OSMnx para garantir que os trajetos a pé seguem ruas e passadeiras reais, e não apenas linhas retas.
* Algoritmos Avançados: Implementações customizadas de A Otimizado*, Dijkstra Multi-Label e ACO (Ant Colony Optimization).

# 📊 Exploração Interativa

Podes testar e visualizar o motor de roteamento diretamente através do nosso Jupyter Notebook: 👉 [route-optimization-optimized.ipynb](./code/notebook/route-optimization-optimized.ipynb)

# 🛠️ Instalação e Configuração
Para preparar o teu ambiente, instalar as dependências necessárias (Python 3.11+) e configurar os dados GTFS, consulta o nosso guia detalhado:

👉 [Instruções de Instalação e Requisitos](./code/README.md)