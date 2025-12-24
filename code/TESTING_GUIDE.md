# 🧪 Guia de Execução e Interpretação de Testes

**📚 Documentação Relacionada:**
- [USER_GUIDE.md](USER_GUIDE.md) - Guia prático para utilizadores
- [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Detalhes técnicos e arquitetura
- [README.md](../README.md) - Visão geral do projeto

## Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Como Executar os Testes](#como-executar-os-testes)
4. [Compreender os Resultados](#compreender-os-resultados)
5. [Casos de Teste Detalhados](#casos-de-teste-detalhados)
6. [Troubleshooting](#troubleshooting)

---

## Visão Geral

Este guia explica como executar os **22 casos de teste** implementados e interpretar os resultados da comparação entre os três algoritmos de roteamento:

- **A\* (Heurístico):** Rápido, mas com cobertura Pareto ~85%
- **Dijkstra (Exaustivo):** Mais lento, mas garante 100% de cobertura Pareto
- **ACO (Estocástico):** Criativo, cobertura Pareto ~70%, encontra rotas inesperadas

---

## Pré-requisitos

### Instalação

```bash
# 1. Navegar até à pasta de código
cd d:\GIT\MIA\CIN_GRUPO6\code

# 2. Instalar dependências (se não feito)
poetry install

# 3. Ativar ambiente virtual
poetry shell

# 4. Verificar instalação
python --version
```

### Dados Necessários

Os ficheiros GTFS devem estar em `feeds/`. Se não existem, descarregue com:

```bash
# Descarregar dados públicos do Porto (Metro + STCP)
python -m app.utils.loaddata
```

Estrutura esperada:
```
feeds/
  ├── gtfs_metro/              # 🚇 Metro do Porto
  │   ├── stops.txt
  │   ├── stop_times.txt
  │   ├── routes.txt
  │   └── ...
  └── gtfs_stcp/               # 🚌 STCP (Autocarros)
      ├── stops.txt
      ├── stop_times.txt
      └── ...
```

Ver [loaddata.py](app/utils/loaddata.py) para detalhes sobre download e cache.

---

## Como Executar os Testes

### 1. Ver Lista de Todos os Casos

```bash
python -m app.test_cases --list
```

**Saída Esperada:**
```
🟢 TRIVIAL (2 casos)
  TC-1.1: Livraria Bertrand → Torre dos Clérigos (3min, 0.3km)
  TC-1.2: Estação S. Bento → Matosinhos (15min, 6km)

🟡 BAIXA (2 casos)
  TC-2.1: Mercado Bolhão → Ribeira (20min, 2.5km)
  TC-2.2: Casa Música → Livraria Lello (25min, 3.5km)

... (demais grupos)

Total: 22 casos
```

### 2. Executar um Caso Específico

#### Via CLI
```bash
python -m app.test_cases --case TC-3.1
```

**Saída Esperada:**
```
═══════════════════════════════════════════════════════
          TEST CASE: TC-3.1 (MÉDIA COMPLEXIDADE)
═══════════════════════════════════════════════════════

📍 Origem: Santa Apolónia
📍 Destino: Francelos (Vila Nova de Gaia)
🕐 Hora: 09:00:00
📏 Distância esperada: ~12km
⏱️  Tempo esperado: ~40min

─────────────────────────────────────────────────────
       RESULTADOS DO A* (HEURÍSTICO)
─────────────────────────────────────────────────────

✓ Algoritmo: A* Multi-Objetivo
⏱️  Tempo de execução: 3.2 segundos
📊 Número de soluções: 8
✅ Status: OK

─────────────────────────────────────────────────────
       RESULTADOS DO DIJKSTRA (EXAUSTIVO)
─────────────────────────────────────────────────────

✓ Algoritmo: Dijkstra Multi-Label
⏱️  Tempo de execução: 7.5 segundos
📊 Número de soluções: 9
✅ Status: OK

─────────────────────────────────────────────────────
       RESULTADOS DO ACO (ESTOCÁSTICO)
─────────────────────────────────────────────────────

✓ Algoritmo: ACO
⏱️  Tempo de execução: 12.3 segundos
📊 Número de soluções: 7
✅ Status: OK

─────────────────────────────────────────────────────
            COMPARAÇÃO DE ALGORITMOS
─────────────────────────────────────────────────────

Cobertura Pareto (A* vs Dijkstra): 88.9%
  → A* encontrou 8 de 9 soluções ótimas (1 solução perdida)

Cobertura Pareto (Dijkstra vs Dijkstra): 100.0%
  → Dijkstra é referência (ótimo por construção)

Cobertura Pareto (ACO vs Dijkstra): 77.8%
  → ACO encontrou 7 de 9 soluções (2 soluções perdidas)

Tempo Relativo:
  A*:      3.2s (100% = baseline)
  Dijkstra: 7.5s (234% mais lento)
  ACO:     12.3s (384% mais lento)

─────────────────────────────────────────────────────
                RESUMO DETALHADO
─────────────────────────────────────────────────────

Rota 1 (A* + Dijkstra + ACO):
  Tempo: 2340s (39min)
  CO2: 125.5g
  Caminhada: 0.8km
  Descrição: Metro Red → Bus 30

Rota 2 (A* + Dijkstra):
  Tempo: 2520s (42min)
  CO2: 95.3g
  Caminhada: 1.2km
  Descrição: Walk → Metro Blue → Transfer → Bus 35

Rota 3 (Dijkstra apenas):
  Tempo: 2680s (44.7min)
  CO2: 85.1g
  Caminhada: 2.5km
  Descrição: Walk → Metro Blue → Walk

✅ TESTE PASSOU
```

#### Via Python (Notebook/Script)

```python
from app.test_cases import TestCaseEvaluator
from app.services.algoritms.a_star import optimized_multi_objective_routing
from app.services.graph import graph as G  # Grafo global pré-carregado
import time

# Selecionar caso
test_case = TestCaseEvaluator.get_by_id("TC-3.1")

# Extrair origem, destino e hora
origin = test_case['origem']  # ex: "Santa Apolónia"
destination = test_case['destino']  # ex: "Francelos"
start_time_str = test_case['start_time']  # ex: "09:00:00"

# Converter hora para segundos
hours, minutes, seconds = map(int, start_time_str.split(':'))
start_time_sec = hours * 3600 + minutes * 60 + seconds

# Executar A*
print(f"🔍 Testando A* de {origin} para {destination}...")
start = time.time()
solutions_astar = optimized_multi_objective_routing(
    G,
    origin=origin,
    destination=destination,
    start_time_sec=start_time_sec
)
elapsed = time.time() - start

print(f"✓ A* encontrou {len(solutions_astar)} soluções em {elapsed:.2f}s")
for i, sol in enumerate(solutions_astar, 1):
    hours_arr = sol.arrival_sec // 3600
    minutes_arr = (sol.arrival_sec % 3600) // 60
    print(f"  Rota {i}: {sol.total_time//60}min, {sol.total_co2:.1f}g CO2, {sol.total_walk_km:.2f}km a pé")
    print(f"           Chega às {hours_arr:02d}:{minutes_arr:02d}")
```

### 3. Executar Todos os Testes (Batches)

```bash
# Executar todos os 22 testes
python -m app.test_cases
```

**Saída Esperada:**
```
🧪 SISTEMA DE TESTES - 22 Casos Disponíveis
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

🟢 TRIVIAL (2 casos)
   TC-1.1: Livraria Bertrand → Torre dos Clérigos
   TC-1.2: Estação S. Bento → Matosinhos

🟡 BAIXA (2 casos)
   TC-2.1: Mercado Bolhão → Ribeira
   TC-2.2: Casa Música → Livraria Lello

🟠 MÉDIA (3 casos)
   TC-3.1: Santa Apolónia → Francelos
   TC-3.2: Parque Cidade → Livraria Lello
   TC-3.3: Centro → Espinho

🔴 ALTA (5 casos)
   TC-4.1: Maia → Espinho
   TC-4.2: Arcozelo → Matosinhos
   TC-4.3: Parque Cidade → Vila do Conde (MADRUGADA)
   TC-4.4: Vila do Conde → Maia
   TC-4.5: Periferia → Periferia

🔵 ESPECIAL (5 casos)
   TC-5.1: Torre dos Clérigos → Torre dos Clérigos (Origem=Destino)
   TC-5.2: S. Bento → Vila Nova de Gaia
   TC-5.3: Validação Convergência (A* vs Dijkstra)
   TC-5.4: Extremos CO2
   TC-5.5: ACO Estocástico

⚫ EXTREMO (4 casos)
   TC-6.1: Localização Isolada
   TC-6.2: Madrugada (23:30)
   TC-6.3: Restrições Temporais
   TC-6.4: Casos Edge
```

### 4. Executar por Grupo de Complexidade

```bash
# Apenas testes TRIVIAIS
python -m app.test_cases --group trivial

# Apenas testes de complexidade MÉDIA
python -m app.test_cases --group medium

# Apenas testes EXTREMOS
python -m app.test_cases --group extreme
```

**Nota:** Use `python -m app.test_cases --help` para ver todas as opções disponíveis.

---

## Compreender os Resultados

### Métricas Principais

#### 1. **Cobertura Pareto**

Mede qual percentagem de soluções de um algoritmo são reconhecidas como não-dominadas por outro.

```
Cobertura(A* vs Dijkstra) = 88.9%
```

**Interpretação:**
- ✅ **> 85%:** Muito bom! A* recupera a maioria das soluções ótimas
- ⚠️ **70-85%:** Aceitável, mas há perda de qualidade
- ❌ **< 70%:** Problema! Algoritmo está perdendo soluções importantes

**Cálculo:**
$$\text{Cobertura}(A, B) = \frac{|\text{soluções de A não dominadas por B}|}{|\text{total de soluções em A}|}$$

#### 2. **Tempo de Execução**

Tempo decorrido desde o início até encontrar todas as soluções.

```
A*:      3.2 segundos
Dijkstra: 7.5 segundos (2.3× mais lento)
ACO:     12.3 segundos (3.8× mais lento)
```

**Interpretação:**
- ✅ **A* < 5s:** Normal, heurística é eficiente
- ✅ **Dijkstra < 15s:** Normal, algoritmo exaustivo
- ✅ **ACO < 20s:** Normal, iterações estocásticas

#### 3. **Número de Soluções**

Quantas soluções Pareto-não-dominadas foram encontradas.

```
A*:      8 soluções
Dijkstra: 9 soluções (1 a mais)
ACO:     7 soluções (2 a menos)
```

**Interpretação:**
- ✅ **Variação < 20%:** Normal, flutuação esperada
- ⚠️ **Variação 20-50%:** Possível perda de qualidade
- ❌ **Variação > 50%:** Problema! Algoritmo está falhando

#### 4. **Spread da Fronteira**

Mede a diversidade de trade-offs entre tempo, CO₂ e caminhada.

```
Spread = (tempo_máximo - tempo_mínimo) / tempo_mediano
       = (2800 - 2340) / 2500
       = 460 / 2500
       = 0.184 (18.4%)
```

**Interpretação:**
- ✅ **> 0.3 (30%):** Boa diversidade de rotas
- ⚠️ **0.1-0.3 (10-30%):** Diversidade moderada
- ❌ **< 0.1 (10%):** Fraca diversidade, rotas muito similares

---

### Tabelas de Resultados

#### Formato Estendido: Comparação Completa

```
┌──────┬─────────────┬────────────────┬───────────────┬──────────┬─────────┐
│ Caso │  Algoritmo  │ Tempo (segundos)│ Soluções (n°) │ CO₂ Médio│Cobertura│
├──────┼─────────────┼────────────────┼───────────────┼──────────┼─────────┤
│TC-3.1│ A*          │ 3.2            │ 8             │ 95.5g    │  88.9%  │
│      │ Dijkstra    │ 7.5            │ 9             │ 93.2g    │ 100.0%  │
│      │ ACO         │ 12.3           │ 7             │ 98.1g    │  77.8%  │
└──────┴─────────────┴────────────────┴───────────────┴──────────┴─────────┘
```

#### Interpretação de Cada Coluna

- **Tempo:** Quanto menor, melhor. A* deve ser < Dijkstra < ACO
- **Soluções:** Número de rotas Pareto-ótimas. Dijkstra ≥ A* ≥ ACO em média
- **CO₂ Médio:** Emissão média das soluções. Valores similares entre algoritmos = bom
- **Cobertura:** Dijkstra = 100%, A* ≥ 85%, ACO ≥ 70%

---

## Casos de Teste Detalhados

### Grupo 1: Trivial 🟢

**Objetivo:** Validar correctness básico e casos simples.

#### TC-1.1: Livraria Bertrand → Torre dos Clérigos

```
Localização: Centro do Porto
Distância: 0.3km (caminhada)
Tempo: ~3 minutos
Complexidade: Muito Baixa
```

**Uso:** Testar se o sistema consegue rodar sem crashes.

**Resultado Esperado:**
- ✅ 1-2 soluções apenas
- ✅ Tempo < 1s para todos os algoritmos
- ✅ Cobertura Pareto = 100%

**Possíveis Problemas:**
```
❌ Erro de Módulo não encontrado
   → Confirmar que está no diretório correto:
       cd d:\GIT\MIA\CIN_GRUPO6\code
   → Verificar instalação:
       python -m app.test_cases

❌ Nenhuma rota encontrada
   → Grafo pode não estar carregado
   → Verificar se feeds/ tem dados GTFS:
       python -m app.utils.loaddata
   → Testar com um caso simples (TC-1.1):
       python -m app.test_cases --case TC-1.1

❌ Tempo > 5s para A*
   → Possível problema de performance
   → Verificar métricas do sistema (RAM/CPU)
   → Tentar com caso mais simples primeiro
```

#### TC-1.2: Estação S. Bento → Matosinhos

```
Localização: Porto → Matosinhos
Distância: 6km
Tempo: ~15 minutos
Transporte: Metro linha amarela (direto)
Complexidade: Muito Baixa
```

**Resultado Esperado:**
- ✅ 1-2 soluções (rota direta + alternativas mínimas)
- ✅ Solução direta: ~15min, ~50g CO₂, ~0.1km a pé
- ✅ Cobertura = 100%

---

### Grupo 2: Baixa Complexidade 🟡

**Objetivo:** Testar transferências simples.

#### TC-2.1: Mercado Bolhão → Ribeira

```
Localização: Centro Porto
Distância: 2.5km
Tempo: ~20 minutos
Transferências: 1
Hora: 14:00 (fora de pico)
```

**Resultado Esperado:**
- ✅ 3-5 soluções
- ✅ Tempo: A* ~1s, Dijkstra ~2.5s, ACO ~4s
- ✅ Cobertura A*: ≥ 85%

#### TC-2.2: Casa Música → Livraria Lello

```
Localização: Centro Porto
Distância: 3.5km
Tempo: ~25 minutos
Transferências: 1-2
Hora: 09:00 (hora de pico)
```

**Resultado Esperado:**
- ✅ 4-6 soluções
- ✅ Mais soluções que TC-2.1 por causa da hora de pico
- ✅ Spread > 0.2 (diversidade moderada)

---

### Grupo 3: Média Complexidade 🟠

**Objetivo:** Testar transferências múltiplas e trade-offs claros.

#### TC-3.1: Santa Apolónia → Francelos

```
Localização: Porto → Vila Nova de Gaia
Distância: 12km
Tempo: ~40 minutos
Transferências: 2 esperadas
Hora: 09:00
Trade-off: Tempo vs. CO₂ vs. Caminhada
```

**Resultado Esperado:**
- ✅ 5-10 soluções
- ✅ Spread > 0.2
- ✅ Dijkstra encontra 9-11 soluções
- ✅ A* cobertura ≥ 85%

**Análise de Soluções:**

```
Rota Rápida (Tempo):
  - Metro direta → Bus direto
  - ~35min, ~120g CO₂, ~0.5km a pé

Rota Eco (CO₂):
  - Muita caminhada + um autocarro
  - ~45min, ~60g CO₂, ~3km a pé

Rota Balanced:
  - Metro + Transfer + Bus
  - ~40min, ~95g CO₂, ~1km a pé
```

---

### Grupo 4: Alta Complexidade 🔴

**Objetivo:** Testar casos com múltiplas alternativas.

#### TC-4.1: Maia → Espinho

```
Localização: Periferia Norte → Sul
Distância: 35km
Tempo: ~1 hora
Transferências: 2-3 esperadas
Hora: 11:00
Risco: Muitas alternativas, algoritmos podem divergir
```

**Resultado Esperado:**
- ✅ 6-15 soluções (grande spread)
- ⚠️ A* pode perder algumas soluções (cobertura ~80%)
- ⚠️ ACO pode encontrar rotas criativas

**Observação Especial:**

Este é um caso onde ACO pode brilhar! Pela estocasticidade, pode descobrir rotas pouco óbvias que A* poderia ter descartado por heurística.

#### TC-4.3: Parque Cidade → Vila do Conde (Madrugada)

```
Localização: Porto → Vila do Conde
Distância: 18km
Tempo: ~50 minutos (horário normal)
Hora: 23:30 (MADRUGADA - teste crítico)
Conectividade: MUITO REDUZIDA
Risco: Alguns algoritmos podem estar lentos ou retornar apenas caminhada
```

**Resultado Esperado:**
- ⚠️ Poucas soluções (2-5)
- ⚠️ Pode incluir apenas "walk" (caminhada completa)
- ⚠️ Tempo ACO pode ser elevado (exploração em espaço reduzido)

**Interpretação:**

Se ACO retornar uma solução criativa (ex: autocarro noturno que A* não viu), isso é BÊNÇÃO não maldição!

---

### Grupo 5: Especial 🔵

#### TC-5.1: Rua Clérigos → Torre dos Clérigos (Origem ≈ Destino)

```
Localização: Mesma rua
Distância: 0.1km
Tempo: ~1 minuto
Complexidade: Edge case
```

**Resultado Esperado:**
- ✅ 1 solução (caminhada imediata)
- ✅ Tempo ≈ 60 segundos, CO₂ = 0, Walk = 0.1km
- ❌ NÃO deve crashar nem retornar erro

#### TC-5.3: S. Bento ↔ Vila Nova Gaia (Validação Convergência)

```
Objetivo: Verificar se A* e Dijkstra encontram as MESMAS soluções
Esperado: Cobertura A* vs Dijkstra = 100%
          (ou muito próximo de 100%, ~95%+)
```

**Se Cobertura < 90%:**
```
⚠️ AVISO: A* está a perder soluções ótimas
   Possíveis causas:
   1. Heurística não é admissível
   2. Pruning está muito agressivo
   3. MAX_LABELS_PER_NODE é muito baixo
```

---

## Troubleshooting

### Erro: "ModuleNotFoundError"

```
ModuleNotFoundError: No module named 'app'
```

**Solução:**

1. Verificar diretório de trabalho:
```bash
cd d:\GIT\MIA\CIN_GRUPO6\code
pwd  # ou "cd" no Windows para confirmar
```

2. Verificar instalação de dependências:
```bash
poetry install
poetry shell
```

3. Testar import simples:
```python
cd d:\GIT\MIA\CIN_GRUPO6\code
python -c "from app.test_cases import TestCaseEvaluator; print('✓ OK')"
```

---

### Erro: "GTFS data not found"

```
FileNotFoundError: feeds/gtfs_metro not found
```

**Solução:**

1. Usar `loaddata.py` para descarregar automaticamente:
```bash
python -m app.utils.loaddata
```

2. Verificar estrutura após download:
```bash
ls -la feeds/
# Deve existir: feeds/gtfs_metro/ e feeds/gtfs_stcp/
ls feeds/gtfs_metro/stops.txt  # Validar que ficheiros existem
```

3. Se ainda falta algo, descarregar manualmente:
```bash
# Ver [USER_GUIDE.md](USER_GUIDE.md) Passo 3 para instruções
# https://www.metro.pt/pt/empresa/open-data
# https://www.stcp.pt/pt/empresa/desenvolvimento-aberto
```

---

### Erro: "Algorithm timeout"

```python
TimeoutError: A* execution exceeded 10 seconds
```

**Solução:**

1. Aumentar timeout (em `app/test_cases.py`):
```python
A_STAR_TIMEOUT = 30  # Era 10, agora 30 segundos
```

2. Reduzir MAX_LABELS_PER_NODE (acelera):
```python
MAX_LABELS_PER_NODE = 5  # Era 10, agora 5
# Trade-off: mais rápido, menos preciso
```

3. Verificar se grafo carrega:
```python
from app.services.graph import graph as G
print(f"Grafo carregado: {G.number_of_nodes()} nós")
print(f"Arestas: {G.number_of_edges()}")
```

---

### Aviso: "Low Pareto coverage"

```
⚠️  AVISO: Cobertura Pareto de A* vs Dijkstra = 72% (< 85%)
```

**Causas Possíveis:**

1. **Heurística não é admissível:**
```python
# Verificar em a_star.py
h_distance = euclidean_distance / max_velocity
# Se h > real_cost, a heurística sobrestima!
```

2. **Pruning muito agressivo:**
```python
# Em a_star.py, aumentar epsilon:
epsilon_time = 120  # Era 60, agora 120
```

3. **MAX_LABELS_PER_NODE muito baixo:**
```python
MAX_LABELS_PER_NODE = 15  # Era 10, aumentar para 15
```

---

### Aviso: "ACO cobertura muito baixa"

```
⚠️  AVISO: Cobertura ACO vs Dijkstra = 45% (< 70%)
```

**Isso é ESPERADO para ACO!**

ACO é estocástico e explorativo. Cobertura 70% é o mínimo esperado. Se for muito mais baixo:

```python
# Aumentar número de iterações
num_iterations = 50  # Era 20, agora 50

# Aumentar número de formigas
num_ants = 50  # Era 30, agora 50
```

---

### Erro: "Memory exhausted"

```python
MemoryError: Unable to allocate X GB
```

**Solução:**

1. Reduzir MAX_LABELS:
```python
MAX_LABELS_PER_NODE = 5  # Era 10
MAX_LABELS_DIJKSTRA = 4  # Era 8
```

2. Executar testes um por um (não todos simultâneos)

3. Limpar cache entre testes:
```python
import gc
gc.collect()  # Forçar garbage collection
```

---

## Visualização de Resultados

### 1. Relatório no Terminal

Os testes exibem relatórios formatados diretamente:
```
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
          TEST CASE: TC-3.1 (MÉDIA COMPLEXIDADE)
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

📍 Origem: Santa Apolónia
📍 Destino: Francelos
⏱️  Tempo esperado: ~40min

RESULTADOS DO A*:
  ✓ Tempo: 3.2s
  📊 Soluções: 8
  🏃 Mais rápida: 2340s (39min)
  🌱 Mais eco: 125.5g CO2
```

### 2. Visualização de Rotas em Mapa

Use `map.py` para visualizar soluções graficamente:

```python
from app.utils.map import visualize_multiple_routes
from app.services.algoritms.a_star import optimized_multi_objective_routing
from app.services.graph import graph as G

# Calcular rotas
solutions = optimized_multi_objective_routing(
    G,
    origin="Santa Apolónia",
    destination="Francelos",
    start_time_sec=32400
)

# Visualizar em mapa interativo
map_obj = visualize_multiple_routes(
    solutions,
    graph=G,
    title="Teste TC-3.1: Fronteira Pareto"
)
map_obj.save("test_tc_3_1.html")
print("✓ Mapa salvo em: test_tc_3_1.html")
```

Ver [map.py](app/utils/map.py) para mais detalhes sobre visualização.

---

## Próximos Passos

Depois de executar os testes:

1. ✅ **Análise:** Verificar métricas e relatórios
2. ✅ **Otimização:** Ajustar parâmetros se necessário
3. ✅ **Documentação:** Registar descobertas no README principal
4. ✅ **Publicação:** Incluir resultados em artigo/relatório

---

## Referências

**Documentação Principal:**
- [README.md](../README.md) - Descrição e quick start do projeto
- [USER_GUIDE.md](USER_GUIDE.md) - Guia prático para utilizadores
- [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Arquitetura e implementação

**Código e Utilitários:**
- Algoritmos: `app/services/algoritms/` (a_star.py, dijkstra.py, aco.py)
- Casos de Teste: `app/test_cases.py` (22 casos organizados por complexidade)
- Carregamento de Dados: `app/utils/loaddata.py` (download e cache GTFS)
- Visualização: `app/utils/map.py` (mapas interativos com Folium)
- Grafo Multimodal: `app/services/graph.py` (construção de rede)

**Dados:**
- GTFS Metro: `feeds/gtfs_metro/` (paragens, horários, rotas)
- GTFS STCP: `feeds/gtfs_stcp/` (autocarros Porto)

