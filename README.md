# 🚌 Sistema de Roteamento Multimodal para a Área Metropolitana do Porto

**Projeto CIN - Grupo 6**

| Elemento | Informação |
|----------|-----------|
| PG11605 | Carlos da Mota Bergueira |
| PG59999 | Diego Jefferson Mendes Silva |
| PG42201 | Filipa Araújo Pereira |
| PG7942 | Rui Manuel Martins Marques Rodrigues |

---

## 📋 Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Opções Técnicas de Desenvolvimento](#opções-técnicas-de-desenvolvimento)
3. [Metodologia de Avaliação](#metodologia-de-avaliação)
4. [Conjunto de Casos de Teste](#conjunto-de-casos-de-teste)
5. [Software Utilizado e Justificação](#software-utilizado-e-justificação)
6. [Guia de Instalação](#guia-de-instalação)
7. [Documentação Complementar](#documentação-complementar)
8. [Referências Bibliográficas](#referências-bibliográficas)
9. [Contribuições](#contribuições)
10. [Licença](#licença)

---

<a id="visão-geral-do-projeto"></a>

## 🎯 Visão Geral do Projeto

Este repositório implementa um **motor de roteamento multimodal** que otimiza trajetos na Área Metropolitana do Porto considerando múltiplos critérios:

- **Tempo de viagem** (minimizar)
- **Emissões de CO₂** (minimizar)
- **Distância a pé** (minimizar)

O sistema retorna uma **Fronteira de Pareto** - um conjunto de rotas onde nenhuma é superior em todos os critérios simultaneamente, permitindo ao utilizador escolher baseado nos seus valores pessoais.

### ✨ Características Principais

✅ **Otimização Multi-Objetivo**: Três critérios simultâneos com fronteira Pareto rigorosa  
✅ **Dados Reais**: Integração com GTFS (Metro do Porto, STCP) e OpenStreetMap  
✅ **3 Algoritmos Avançados**: A* Heurístico, Dijkstra Exaustivo, ACO Estocástico  
✅ **Análise Geográfica**: Ruas reais (OSMnx), não linhas retas  
✅ **22 Casos de Teste**: Cobertura de trivial a extremo  
✅ **Framework de Avaliação**: Comparação automática de algoritmos  

---

<a id="opções-técnicas-de-desenvolvimento"></a>

## 🎨 Opções Técnicas de Desenvolvimento

Esta secção descreve as principais decisões arquitectónicas e técnicas tomadas durante o desenvolvimento, com justificação teórica.

### 1. Otimização Multi-Objetivo vs. Mono-Objetivo

**Decisão:** Implementar otimização para **3 critérios simultâneos** (tempo, CO₂, caminhada) em vez de otimizar apenas um objetivo.

**Justificação:**
- **Realismo:** Utilizadores reais têm preferências conflitantes - alguns priorizam velocidade, outros sustentabilidade [1]
- **Pareto Frontier:** Retornar o conjunto de soluções Pareto-ótimas (não-dominadas) permite ao utilizador escolher [2]
- **Teoria de Decisão:** Problema de "many-objective optimization" requer técnicas especializadas [3]
- **Inovação:** A maioria dos sistemas usa apenas tempo; CO₂ + caminhada são diferenciadoras

**Implementação:**
- Classe `Solution` com 3 atributos: `total_time`, `total_co2`, `total_walk_km`
- Função de dominância Pareto: Solução A domina B se A ≤ B em todos critérios (com pelo menos 1 < estrito)
- Pruning por dominância em todos os algoritmos

---

### 2. Abordagem Multi-Algoritmo: A*, Dijkstra e ACO

**Decisão:** Implementar **3 algoritmos diferentes** em vez de escolher apenas um.

**Justificação:**
- **A* (Heurístico):** Rápido (~segundos) usando função admissível; bom trade-off velocidade/qualidade [4]
- **Dijkstra (Exaustivo):** Lento mas GARANTE fronteira Pareto ótima; referência de validação [5]
- **ACO (Estocástico):** Exploração criativa útil em baixa conectividade; inspira-se em comportamentos naturais [6]

**Teorema:** Cada algoritmo tem vantagens:
- A*: Tempo ≤ Dijkstra (heurística poupa expansões)
- Dijkstra: Qualidade ≥ A* (análise completa)
- ACO: Diversidade ≥ A*/Dijkstra (exploração não-determinística)

**Implementação:**
- Interface comum: `routing_algorithm(graph, origin, destination, start_time) → List[Solution]`
- Comparação automática via `evaluation_framework.py`
- 22 casos de teste para validação relativa

---

### 3. Grafo Multimodal com Integração GTFS + OpenStreetMap

**Decisão:** Integrar **dois grafos diferentes** em um único grafo híbrido.

**Justificação:**
- **GTFS (Transportes Públicos):** Nós = paragens, arestas = viagens (com horários)
- **OpenStreetMap (Ruas):** Nós = interseções, arestas = ruas (sem horários)
- **Sincronização Temporal:** Nós de transferência com restrições de espera (min-transfer-time) [7]

**Desafios Resolvidos:**
1. **Matching paragens ↔ ruas:** Usar OSMnx para encontrar nó mais próximo (< 100m)
2. **Custos heterogéneos:** Tempo em transporte público ≠ tempo a pé ≠ tempo em carro
3. **Constraints temporais:** Respeitar calendários GTFS (dias úteis, fins de semana, feriados)

**Implementação:**
```python
# Pseudo-código
G = MultiGraph()
# Adicionar nós GTFS
for paragem in gtfs.stops:
    G.add_node(paragem.stop_id, type='transit_stop', coords=...)
# Adicionar arestas GTFS (com horários)
for trip in gtfs.trips:
    for (stop_i, stop_j, time_diff) in trip:
        G.add_edge(stop_i, stop_j, type='transit', duration=time_diff, ...)
# Adicionar nós OSM
for intersecao in osm.nodes:
    G.add_node(intersecao.id, type='street_node', coords=...)
# Conectar GTFS ↔ OSM
for paragem in gtfs.stops:
    closest_osm = find_nearest(osm.nodes, paragem)
    if distance(paragem, closest_osm) < 100m:
        G.add_edge(paragem, closest_osm, type='transfer', ...)
```

---

### 4. Dados GTFS Reais (Metro do Porto + STCP)

**Decisão:** Usar dados **GTFS reais e públicos** em vez de dados sintéticos.

**Justificação:**
- **Validação Realista:** Testar em dados reais detecta problemas (horários raros, transferências complexas) [8]
- **Reprodutibilidade:** Dados GTFS são versionados e públicos
- **Aplicabilidade:** Sistema pronto para usar em produção
- **Padrão Industrial:** GTFS é standard da Google para transportes [9]

**Fontes:**
- Metro do Porto: 6 linhas, ~95 paragens, data/hora precisa
- STCP: 100+ linhas, ~1000 paragens de autocarro

**Nota:** Dados de 2024; atualizar se houver mudanças operacionais

---

### 5. Heurística Admissível para A* Multi-Objetivo

**Decisão:** Usar **distância euclidiana / velocidade máxima** como heurística admissível.

**Justificação Teórica:**
- Uma heurística $h$ é admissível se $h(n) \leq h^*(n)$ (não sobrestima o custo real) [10]
- Para múltiplos objetivos, cada heurística deve ser admissível independentemente
- Distância euclidiana / velocidade_máxima garante limite inferior no tempo

**Fórmula:**
$$h(n) = \frac{\text{distância euclidiana}(n, \text{destino})}{\text{velocidade máxima permitida}}$$

Onde velocidade máxima = max(velocidade metro, velocidade autocarro, velocidade a pé)

**Propriedade:** Esta heurística é **consistente** (satisfaz desigualdade triangular), logo A* é ótimo em grafos de custo não-negativo [11]

---

### 6. Fronteira de Pareto com Pruning por Dominância

**Decisão:** Em vez de retornar TODAS as rotas possíveis, manter apenas soluções **não-dominadas**.

**Justificação:**
- **Eficiência:** Reduz explosão combinatória (uma solução dominada nunca será preferida)
- **Clareza ao utilizador:** Apresentar 5-15 rotas é mais útil que 100+
- **Otimalidade:** Pareto frontier preserva todas as soluções "interessantes"

**Implementação:**
```
Função dominates(sol_a, sol_b):
    return (sol_a.time ≤ sol_b.time AND
            sol_a.co2 ≤ sol_b.co2 AND
            sol_a.walk_km ≤ sol_b.walk_km AND
            PELO MENOS UM <)

Função add_solution_with_diversity(solution, frontier):
    # Remover todas as soluções dominadas por solution
    frontier = [s for s in frontier if NOT dominates(solution, s)]
    # Adicionar solution se não for dominada
    if NOT any(dominates(s, solution) for s in frontier):
        frontier.append(solution)
    return frontier
```

---

### 7. Análise Geográfica com Distâncias Reais (não Euclidianas)

**Decisão:** Calcular distâncias seguindo **ruas reais** via OpenStreetMap em vez de linhas retas.

**Justificação:**
- **Realismo:** Distância euclidiana pode ser 30-50% menor que distância real [12]
- **Routing:** Um utilizador a pé não pode atravessar edifícios; precisa de ruas
- **Integração:** OSMnx fornece acesso fácil ao grafo de ruas

**Implementação:**
- `graph.py` carrega grafo de ruas com `osmnx.graph_from_bbox()`
- Usa algoritmo Dijkstra de NetworkX para caminho mais curto a pé
- Distância = soma dos comprimentos das arestas das ruas

---

### 8. Estimativa de Emissões CO₂ por Modo de Transporte

**Decisão:** Atribuir **emisões específicas** para cada modo (metro, autocarro, a pé).

**Justificação:**
- **Sustentabilidade:** CO₂ é proxy para impacto ambiental [13]
- **Realismo:** Metro tem ~70g CO₂/passageiro/km; autocarro ~100g; a pé ~0g [14]
- **Comparação:** Permite trade-off quantitativo entre velocidade e sustentabilidade

**Fórmula:**
$$\text{CO2}(rota) = \sum_{\text{segmento}} (\text{distância} \times \text{emissão\_específica})$$

**Valores por modo:**
| Modo | Emissão (g/km) | Fonte |
|------|---|---|
| Metro | 70 | LIPASTO/VTT [15] |
| Autocarro | 100 | LIPASTO/VTT |
| Caminhada | 0 | N/A |
| Bicicleta (futuro) | 0 | N/A |

---

### 9. Estrutura de Dados: Classes Solution e GraphRoute

**Decisão:** Encapsular em **classes Python orientadas a objetos** em vez de dicionários/tuples.

**Justificação:**
- **Type Safety:** Atributos tipados; IDE autocomplete [16]
- **Métodos:** Funções como `dominates()`, `get_heuristic()` vinculadas aos dados
- **Serialização:** Fácil converter para JSON/CSV para persistência
- **Extensibilidade:** Adicionar novos atributos sem quebrar assinaturas de funções

**Classes:**
```python
@dataclass
class Solution:
    total_time: int           # segundos
    total_co2: float          # gramas
    total_walk_km: float      # quilómetros
    arrival_sec: int          # segundos desde meia-noite
    path: List[dict]          # traçado detalhado
    
    def dominates(self, other: 'Solution') -> bool:
        """Retorna True se esta solução domina outra"""
        ...

@dataclass
class GraphRoute:
    """Grafo multimodal com métodos para roteamento"""
    ...
```

---

### 10. Framework de Avaliação Comparativa

**Decisão:** Criar **framework automático** para comparar os 3 algoritmos em 22 casos de teste.

**Justificação:**
- **Validação:** Verificar se A* vs Dijkstra convergem (devem ter mesmas soluções Pareto)
- **Benchmarking:** Medir tempo de execução, número de soluções, qualidade
- **Reprodutibilidade:** Testes automáticos evitam enviesamentos manuais [17]
- **Documentação:** Resultados servem como evidência científica das escolhas

**Métrica de Comparação:** Cobertura Pareto
$$\text{Cobertura}(A, B) = \frac{|\{s_A \in A : \not\exists s_B \in B, s_B \text{ domina } s_A\}|}{|A|}$$

Idealmente: A* ≥ 0.8, Dijkstra = 1.0, ACO ≥ 0.7

---

### 11. Casos de Teste com Múltiplos Níveis de Complexidade

**Decisão:** Criar **22 casos de teste organizados em 6 grupos** de complexidade crescente.

**Justificação:**
- **Cobertura:** Trivial → Extremo cobre espectro de cenários
- **Validação:** Casos triviais verificam correctness; casos extremos testam robustez
- **Investigação:** Identificar "pontos de ruptura" onde algoritmos falham

**Grupos:**
1. **Trivial (2 casos):** Distância <1km, sem transportes públicos
2. **Baixa (2 casos):** 1-5km, máximo 1 transferência
3. **Média (3 casos):** 5-15km, 1-2 transferências
4. **Alta (3 casos):** 15-40km, múltiplas alternativas
5. **Especial (3 casos):** Edge cases (origem=destino, horário noturno)
6. **Extrema (2 casos):** Madrugada, baixíssima conectividade

---

### 12. API REST com FastAPI

**Decisão:** Expor sistema via **API HTTP REST** em vez de apenas CLI.

**Justificação:**
- **Integração:** Permite consumo por aplicações web/mobile
- **Escalabilidade:** ASGI suporta múltiplos clientes concorrentes
- **Padrão:** REST é standard da indústria para APIs [18]
- **Documentação:** FastAPI gera Swagger/OpenAPI automaticamente

**Endpoint implementado:**
```
GET /geocode?address=Torre%20dos%20Clérigos&city=Porto&country=Portugal
→ {"lat": 41.1438, "lon": -8.6290}
```

Futura expansão:
```
POST /route
Body: {origin: [lat, lon], destination: [lat, lon], start_time: "HH:MM:SS"}
Response: {routes: [Solution, ...]}
```

---

### 13. Documentação Tripla: Manual + Teste + Técnica

**Decisão:** Criar **3 ficheiros de documentação complementares**.

**Justificação:**
- **MANUAL_UTILIZADOR.md:** Guia prático (como instalar, como usar)
- **TESTING_GUIDE.md:** Como executar e interpretar testes
- **code/README.md:** Documentação técnica aprofundada
- **Main README.md:** Visão geral + decisões (este ficheiro)

**Teoria:** "Documentation at Multiple Levels" melhora adoção e manutenibilidade [19]

---

### Resumo das Opções Técnicas

| Opção | Escolha | Justificação-chave |
|-------|---------|-------------------|
| Otimização | Multi-Objetivo (3 critérios) | Realismo + Pareto frontier |
| Algoritmos | A* + Dijkstra + ACO | Velocidade + Qualidade + Criatividade |
| Grafo | Multimodal (GTFS + OSM) | Realista + Abrangente |
| Dados | GTFS reais (Metro + STCP) | Validação real + Reprodutível |
| Heurística | Distância / Velocidade | Admissível + Consistente |
| Pruning | Pareto dominância | Eficiente + Útil ao utilizador |
| Geo | Distâncias reais (OSM) | Realista (vs euclidiana) |
| CO₂ | Emissões específicas/modo | Comparação quantitativa |
| Estrutura | Classes OOP (Solution, Graph) | Type-safe + Extensível |
| Avaliação | Framework automático | Validação científica |
| Testes | 22 casos × 6 complexidades | Cobertura abrangente |
| API | REST com FastAPI | Integração + Escalabilidade |
| Docs | 4 ficheiros em cascata | Acessibilidade múltipla |

---

<a id="metodologia-de-avaliação"></a>

## 🔬 Metodologia de Avaliação

Esta secção descreve rigorosamente como o sistema é avaliado, incluindo a definição formal do problema, os algoritmos utilizados, a parametrização, e os critérios de convergência.

### Definição Formal do Problema

**Problema de Roteamento Multimodal Multi-Objetivo:**

Dado:
- Grafo multimodal $G = (V, E)$ onde:
  - $V = V_{transit} \cup V_{street}$ (paragens de transporte + interseções de rua)
  - $E = E_{transit} \cup E_{walk}$ (viagens públicas + caminhos a pé)
- Origem $s \in V$ e destino $d \in V$
- Tempo de partida $t_{start}$

Encontrar o conjunto $S^*$ de soluções Pareto-ótimas onde cada $sol \in S^*$ minimize:
- $f_1(sol) = $ tempo total em segundos
- $f_2(sol) = $ emissões de CO₂ em gramas
- $f_3(sol) = -$ distância a pé em quilómetros (maximizar exercício)

Sujeito a:
- Respeitar horários GTFS (calendários, horários de paragem)
- Não revisitar o mesmo nó (evitar ciclos)
- Caminhos a pé respeitarem rua reais (grafo OSM)

**Definição de Dominância Pareto:**

Solução $a$ domina $b$ iff:
$$f_1(a) \leq f_1(b) \text{ AND } f_2(a) \leq f_2(b) \text{ AND } f_3(a) \geq f_3(b)$$
E pelo menos uma desigualdade é **estrita**.

Notação: $a \succ b$

---

### Codificação de Soluções

**Classe Solution:**

```python
@dataclass
class Solution:
    total_time: int           # [segundos] Tempo acumulado desde partida
    total_co2: float          # [gramas] Emissões de CO2 totais
    total_walk_km: float      # [quilómetros] Distância cumulativa a pé
    arrival_sec: int          # [segundos] Hora de chegada (segundos desde meia-noite)
    path: List[Tuple]         # [(node_id, trip_info, arrival_time), ...]
```

**Traçado (Path):**

Cada elemento do path é uma tupla `(node, info, arrival_time)`:
- `node`: ID do nó no grafo (paragem de transporte ou interseção de rua)
- `info`: Identificador da viagem ou "transfer" (ou "start")
- `arrival_time`: Hora de chegada neste nó em segundos

**Exemplo de Solução:**
```
Rota: Livraria Bertrand → Clérigos (9:00)
  Path: [
    (node_bertrand, 'start', 32400),
    (node_clerigos, 'transfer', 32580),
  ]
  Tempo: 180s (3 minutos)
  CO2: 0g (apenas a pé)
  Walk: 0.3km
```

---

### Função Objetivo

O sistema não otimiza uma única função ponderada, mas mantém **todas as soluções não-dominadas**:

$$\text{Minimize: } \begin{cases} f_1(x) = \text{total\_time} \\ f_2(x) = \text{total\_co2} \\ f_3(x) = -\text{total\_walk\_km} \end{cases}$$

**Justificação:**
- Abordagem Pareto preserva toda a informação de trade-off
- Utilizador escolhe baseado em preferências (não predeterminadas) [1]
- Evita bias introduzido por pesos ad-hoc

**Propriedade:** Cada solução no resultado é **não-dominada localmente** (entre soluções mantidas) e idealmente **não-dominada globalmente** (verdadeira fronteira Pareto).

---

### Algoritmos de Roteamento

#### 1. A* Multi-Objetivo (Heurístico)

**Objetivo:** Encontrar rotas rapidamente (~segundos) usando heurística admissível.

**Pseudocódigo:**

```
A*(G, s, d, t_start):
  OPEN ← {initial_solution(s)}
  CLOSED ← {}
  max_labels_per_node ← 10
  epsilon_time ← 120 segundos
  
  while OPEN ≠ ∅:
    u_sol ← extract_min_by(OPEN, f = g + h)
    
    if u_sol.node == d:
      CLOSED ← add_pareto_diverse(CLOSED, u_sol, epsilon_time)
      continue
    
    for neighbor v in G.neighbors(u_sol.node):
      if v not in u_sol.path:  // Evitar ciclos
        t_cost, c_cost, w_cost ← get_edge_costs(u_sol.node → v)
        
        v_sol.time ← u_sol.time + t_cost
        v_sol.co2 ← u_sol.co2 + c_cost
        v_sol.walk ← u_sol.walk + w_cost
        
        h_v_t, h_v_c ← heuristic(v, d)  // Admissível
        f_v ← (v_sol.time + h_v_t, v_sol.co2 + h_v_c)
        
        if not dominated_by_any(v_sol, labels[v]):
          labels[v] ← add_pareto_diverse(labels[v], v_sol, max_10)
          OPEN.push((f_v, v_sol))
  
  return CLOSED
```

**Parâmetros:**

| Parâmetro | Valor | Justificação |
|-----------|-------|-------------|
| `MAX_LABELS_PER_NODE` | 10 | Balanço: manter diversidade sem explosão combinatória |
| `TIME_WINDOW_EPSILON` | 120s | Agrupar soluções muito semelhantes em tempo |
| `RELAXED_PRUNING_FACTOR` | 1.5 | Permitir soluções até 50% mais lentas (evita descartar criativas) |

**Heurística Admissível:**

$$h(v) = \left( \frac{\text{distância\_euclidiana}(v, d)}{v_{max}} \times 3600, \quad \frac{\text{distância\_euclidiana}(v, d)}{50} \times 40 \right)$$

Onde:
- $v_{max} = 50$ km/h (velocidade máxima assumida)
- Fator CO₂ do metro = 40 g/km (mínimo para qualquer transporte)
- Resultado: **admissível** (nunca sobrestima tempo real)

**Complexidade:**
- Tempo: O(E × labels × log(labels)) ≈ O(E × 10 × log(10))
- Espaço: O(V × labels) = O(V × 10)
- Prática: ~2-5 segundos para redes de 10k nós

---

#### 2. Dijkstra Multi-Label (Exaustivo)

**Objetivo:** Garantir convergência para a verdadeira fronteira Pareto (referência).

**Pseudocódigo:**

```
Dijkstra_Multi(G, s, d, t_start):
  CLOSED ← {}
  labels ← {v: [] for v in V}
  pq ← [(0, 0, initial_solution(s))]
  
  while pq ≠ ∅:
    g_t, g_c, u_sol ← pq.pop()  // Expansão por custo real (sem heurística)
    
    if u_sol.node == d:
      CLOSED ← add_pareto(CLOSED, u_sol)
      continue
    
    for v in G.neighbors(u_sol.node):
      if v not in visited:
        t_cost, c_cost, w_cost ← get_edge_costs(...)
        v_sol.time ← u_sol.time + t_cost
        v_sol.co2 ← u_sol.co2 + c_cost
        
        // Teste de dominância RIGOROSA
        if not dominated(v_sol, labels[v]):
          labels[v] ← add_pareto(labels[v], v_sol)
          pq.push((v_sol.time, v_sol.co2, v_sol))
  
  return CLOSED
```

**Parâmetros:**

| Parâmetro | Valor | Justificação |
|-----------|-------|-------------|
| `MAX_LABELS` | 8 | Mais apertado que A*; Dijkstra é exaustivo |
| `EPSILON` | 60s | Tolerância temporal para evitar explosão de labels |

**Propriedade Teórica:** 
Dijkstra sem heurística $h \equiv 0$ expande sempre o nó com menor custo real acumulado. Isto garante **optimalidade em grafos com pesos não-negativos** [2].

No contexto multi-objetivo:
- **Garantia:** Encontra todas as soluções não-dominadas (se espaço/tempo permitirem)
- **Desvantagem:** Mais lento (factor 2-3× vs A*)

---

#### 3. ACO (Ant Colony Optimization)

**Objetivo:** Exploração estocástica; encontrar rotas criativas em baixa conectividade.

**Pseudocódigo:**

```
ACO(G, s, d, t_start, n_ants=30, n_iter=20):
  pheromone ← {e: 0.1 for e in E}
  global_pareto ← []
  
  for iteration in 1..n_iter:
    iteration_solutions ← []
    
    for ant in 1..n_ants:
      current ← s
      visited ← {s}
      path ← [s]
      
      for step in 1..max_steps:
        if current == d:
          break
        
        // Construção probabilística
        valid_neighbors ← [v for v in neighbors(current) if v ∉ visited]
        
        if valid_neighbors = ∅:
          break
        
        probabilities ← []
        for v in valid_neighbors:
          t_cost ← get_edge_costs(current → v)
          h_v ← heuristic(v, d)  // Visibilidade = 1/(t_cost + h_v)
          tau_cv ← pheromone[(current, v)]
          
          prob_v ← (tau_cv)^α × (1/(t_cost+h_v))^β
          probabilities.append(prob_v)
        
        // Seleção por Roleta
        v ← select_by_probability(valid_neighbors, normalize(probabilities))
        
        current ← v
        visited.add(v)
        path.append(v)
      
      if current == d:
        sol ← create_solution(path, t_start)
        iteration_solutions.append(sol)
    
    // Actualizar fronteira global
    for sol in iteration_solutions:
      global_pareto ← add_pareto(global_pareto, sol)
    
    // Evaporação de feromónios
    for edge in E:
      pheromone[edge] ← pheromone[edge] × (1 - ρ)
    
    // Depósito de feromónios (apenas soluções Pareto)
    for sol in global_pareto:
      reward ← Q / (sol.total_time / 60)  // Inversamente proporcional ao tempo
      for edge in sol.path:
        pheromone[edge] ← pheromone[edge] + reward
  
  return global_pareto
```

**Parâmetros:**

| Parâmetro | Valor | Descrição | Justificação |
|-----------|-------|-----------|-------------|
| `ALPHA` | 1.0 | Peso do feromónio | Balanço entre exploração + memória da população |
| `BETA` | 3.0 | Peso da heurística (visibilidade) | Focado no destino (BETA > ALPHA) [3] |
| `RHO` | 0.1 | Taxa de evaporação | Esquecer soluções antigas (ρ=0.1 = 10% evaporação/iter) |
| `Q` | 100 | Constante de depósito | Escala da recompensa de feromónios |
| `num_ants` | 30 | Formigas por iteração | Suficiente para exploração (30 = ~300 caminhos tentados) |
| `num_iterations` | 20 | Iterações do algoritmo | 20 iterações ≈ 600 tentativas totais |

**Heurística de Visibilidade:**

$$\text{visibility}(v) = \frac{1}{t\_cost + h\_v + 1}$$

Onde:
- $t\_cost$ = tempo real da aresta
- $h\_v$ = distância estimada ao destino
- $+1$ evita divisão por zero

**Probabilidade de Transição:**

$$P(current \to v) = \frac{\tau(current, v)^{\alpha} \times (visibility(v))^{\beta}}{\sum_{u \in valid} \tau(current, u)^{\alpha} \times (visibility(u))^{\beta}}$$

**Algoritmo Local (Deposição):**

Apenas soluções **Pareto-ótimas** depositam feromónios (não todos os caminhos):

$$\Delta\tau = \frac{Q}{sol.total\_time / 60.0}$$

Isto reforça rotas boas e evita convergência prematura [4].

---

### Critérios de Convergência

#### A*
- Termina quando fila OPEN vazia
- Todas as soluções ao destino foram colectadas
- **Tempo típico:** 2-5 segundos (Porto metro-area)

#### Dijkstra
- Termina quando fila vazia
- **Propriedade:** Expansões mais conservadoras que A*
- **Tempo típico:** 5-15 segundos (Porto metro-area)
- **Garantia:** Fronteira Pareto ótima (com máx labels=8)

#### ACO
- Termina após N iterações (20 por padrão)
- Não há garantia de otimalidade
- **Tempo típico:** 10-20 segundos
- **Benefício:** Encontra rotas criativas (especialmente útil em madrugadas/baixa conectividade)

---

### Gestão de Labels e Pruning

**Problema:** Sem limite de soluções por nó, o espaço de estados explode.

**Solução:** Manter apenas as **soluções não-dominadas** (labels) em cada nó.

**Algoritmo `add_solution_with_diversity`:**

```python
def add_solution_with_diversity(frontier, candidate, max_labels=10, epsilon=120):
    """
    Adiciona candidate à fronteira se não for dominada.
    Remove soluções dominadas por candidate.
    """
    # 1. Verificar dominância em nível de tempo (rápido)
    if epsilon > 0:
        dominated = [s for s in frontier 
                     if abs(s.total_time - candidate.total_time) < epsilon
                     and s.dominates(candidate)]
        if dominated:
            return frontier, False  # Candidate é dominada
    
    # 2. Remover soluções dominadas por candidate
    frontier = [s for s in frontier if not candidate.dominates(s)]
    
    # 3. Adicionar candidate se espaço disponível
    if len(frontier) < max_labels:
        frontier.append(candidate)
        return frontier, True
    
    # 4. Se cheio, só adicionar se melhor que pior solução
    if candidate better_than worst_in_frontier:
        frontier.remove(worst)
        frontier.append(candidate)
        return frontier, True
    
    return frontier, False
```

**Impacto:**

| `epsilon` | Efeito | Quando usar |
|-----------|--------|-----------|
| 0 | Sem agrupamento; máxima precisão | Dijkstra (exaustivo) |
| 60-120s | Agrupa soluções semelhantes | A* (equilíbrio) |
| 300+s | Muito agressivo; descarta opções | Nunca (risco) |

---

### Métricas de Avaliação

Para cada teste de roteamento, colectam-se:

#### 1. Cobertura Pareto
$$\text{Cobertura}_{A \text{ vs } B} = \frac{|\{s_A \in A : \not\exists s_B \in B, s_B \succ s_A\}|}{|A|}$$

- A* vs Dijkstra: Idealmente ≥ 0.85 (A* perde 15% pela heurística)
- Dijkstra: 1.0 (ótimo por construção)
- ACO: ≥ 0.70 (estocástico; menos garantido)

#### 2. Tempo de Execução
- **A*:** < 5 segundos (padrão)
- **Dijkstra:** < 15 segundos (padrão)
- **ACO:** < 20 segundos (padrão)

#### 3. Número de Soluções
- **Trivial:** 1-2 rotas
- **Baixa:** 3-5 rotas
- **Média:** 5-10 rotas
- **Alta:** 10-20 rotas
- **Extrema:** 2-5 rotas (conectividade reduzida)

#### 4. Spread da Fronteira
$$\text{Spread}_{tempo} = \frac{\max(t) - \min(t)}{\text{mediana}(t)}$$

Idealmente > 0.3 (diversidade de trade-off)

---

### Casos de Teste e Complexidade

**22 Casos de Teste** organizados por complexidade:

#### Grupo 1: Trivial (2 casos)
- **TC-1.1:** Caminhada <500m (3 min)
- **TC-1.2:** Transporte direto, 1 paragem

#### Grupo 2: Baixa (2 casos)
- **TC-2.1:** 1-2 km, máximo 1 transferência
- **TC-2.2:** 3-5 km, hora de pico

#### Grupo 3: Média (3 casos)
- **TC-3.1:** 10-15 km, 2 transferências obrigatórias
- **TC-3.2:** Periferia com baixa conectividade
- **TC-3.3:** Trade-off claro (rápido vs eco)

#### Grupo 4: Alta (3 casos)
- **TC-4.1:** 30-40 km, múltiplas alternativas
- **TC-4.2:** Hora de pico com muitos hubs
- **TC-4.3:** Madrugada (conectividade mínima)

#### Grupo 5: Especial (3 casos)
- **TC-5.1:** Origem = Destino (edge case)
- **TC-5.2:** Máxima diversidade Pareto
- **TC-5.3:** Validação A* vs Dijkstra equivalência

#### Grupo 6: Extrema (2 casos)
- **TC-6.1:** Origem = Destino
- **TC-6.2:** Horário noturno (23:30)

---

### Framework de Avaliação Comparativa

**Classe `ComparativeEvaluator`:**

```python
class ComparativeEvaluator:
    def run_single_test(self, test_case, algorithms=['a_star', 'dijkstra', 'aco']):
        """Executa um caso de teste com os 3 algoritmos"""
        
        # 1. Geocodificar origem/destino
        origin = geocode(test_case['origem'])
        destination = geocode(test_case['destino'])
        start_time = parse_time(test_case['start_time'])
        
        # 2. Executar cada algoritmo
        for algo in algorithms:
            start = time.time()
            routes = algo(graph, origin, destination, start_time)
            elapsed = time.time() - start
            
            # Coletar métricas
            metrics[algo] = {
                'num_solutions': len(routes),
                'execution_time': elapsed,
                'pareto_coverage': compute_coverage(routes, dijkstra_reference),
                'avg_time': mean([r.total_time for r in routes]),
                'avg_co2': mean([r.total_co2 for r in routes]),
                ...
            }
        
        return TestCaseResult(test_case, metrics)
    
    def print_comparison_table(self, results):
        """Exibe tabela de comparação"""
        ...
    
    def export_results_json(self, results, filename):
        """Salva resultados para análise estatística"""
        ...
```

---

### Justificação das Escolhas

#### Por que 3 Algoritmos?

1. **A* = Velocidade prática** - Heurística reduz expansões desnecessárias [5]
2. **Dijkstra = Garantia científica** - Prova de optimalidade em grafos de peso não-negativo [2]
3. **ACO = Exploração criativa** - Estocástico; encontra soluções inesperadas [6]

#### Por que estes Parâmetros?

- **MAX_LABELS_PER_NODE = 10 (A*):** Mais que 10 soluções por nó é raro; <10 perde qualidade
- **MAX_LABELS = 8 (Dijkstra):** Mais conservador; Dijkstra é exaustivo
- **num_ants = 30:** ~300 trajetos tentados por iteração; suficiente para exploração
- **BETA = 3.0 (ACO):** Focado no destino; evita divagações excessivas

#### Por que Pareto (não pesos)?

A abordagem Pareto:
- ✅ Preserva toda a informação de trade-off
- ✅ Não requer calibração de pesos (ad-hoc)
- ✅ Adequada para decisão multi-critério [1]
- ❌ Mais computacionalmente custosa (mas aceitável para redes de ~10k nós)

---

<a id="conjunto-de-casos-de-teste"></a>

## 🧪 Conjunto de Casos de Teste

O sistema é validado através de **22 casos de teste** cuidadosamente seleccionados, cobrindo a Área Metropolitana do Porto com diversos graus de complexidade.

### Organização dos Casos

Os casos estão organizados em **6 grupos** por complexidade crescente:

#### **Grupo 1: Trivial (2 casos)** 🟢

Testes de validação básica.

| Caso | Origem | Destino | Dist. | Tempo | Descrição |
|------|--------|---------|-------|-------|-----------|
| TC-1.1 | Livraria Bertrand | Torre dos Clérigos | 0.3km | 3min | Apenas caminhada |
| TC-1.2 | Estação S. Bento | Matosinhos | 6km | 15min | Transporte direto (sem transferência) |

**Propriedade:** Uma única solução ou muito poucas opções. Valida correctness básico.

---

#### **Grupo 2: Baixa Complexidade (2 casos)** 🟡

Rotas simples com 1 transferência ou trajeto direto.

| Caso | Origem | Destino | Dist. | Tempo | Descrição |
|------|--------|---------|-------|-------|-----------|
| TC-2.1 | Mercado Bolhão | Ribeira | 2.5km | 20min | Off-peak, 1 transferência |
| TC-2.2 | Casa Música | Livraria Lello | 3.5km | 25min | Hora de pico, múltiplas rotas |

**Propriedade:** 3-8 soluções na fronteira Pareto. Trade-off leve entre tempo/CO2.

---

#### **Grupo 3: Média Complexidade (3 casos)** 🟠

Rotas interurbanas com 2 transferências e conectividade moderada.

| Caso | Origem | Destino | Dist. | Tempo | Descrição |
|------|--------|---------|-------|-------|-----------|
| TC-3.1 | Santa Apolónia | Francelos (Gaia) | 12km | 40min | 2 transferências, trade-off T/CO2 |
| TC-3.2 | Maia | Hospital S. João | 12km | 45min | Origem periférica, baixa conectividade |
| TC-3.3 | Exponor (Matosinhos) | Serralves (Porto) | 5km | 30min | Tempo vs Sustentabilidade |

**Propriedade:** 5-10 soluções. Começa a haver diversidade significativa. ACO pode encontrar rotas criativas.

---

#### **Grupo 4: Alta Complexidade (3 casos)** 🔴

Rotas longas com múltiplas alternativas ou contextos desafiantes.

| Caso | Origem | Destino | Dist. | Tempo | Descrição |
|------|--------|---------|-------|-------|-----------|
| TC-4.1 | Maia | Espinho (Aveiro) | 35km | 1h | Longa, múltiplas alternativas |
| TC-4.2 | Campanhã | Gaia Centre | 8km | 40min | Hora de pico, muitos hubs |
| TC-4.3 | Parque Cidade | Vilar do Conde | 18km | 50min | Madrugada (6h), conectividade mínima |

**Propriedade:** 6-15 soluções. Algoritmos divergem. ACO vantajoso em TC-4.3.

---

#### **Grupo 5: Especial (3 casos)** 🔵

Edge cases e validação de comportamentos esperados.

| Caso | Origem | Destino | Dist. | Tempo | Descrição |
|------|--------|---------|-------|-------|-----------|
| TC-5.1 | Rua Clérigos | Torre Clérigos | 0.1km | 1min | Origem ≈ Destino |
| TC-5.2 | Bolhão | Gaia Centre | 7km | 30min | Máxima diversidade Pareto |
| TC-5.3 | S. Bento | Vila Nova Gaia | 4km | 20min | A* vs Dijkstra convergência |

**Propriedade:** 
- TC-5.1: Testa robustez (origem=destino)
- TC-5.2: Valida que fronteira Pareto é rica em trade-offs
- TC-5.3: Verifica se A* e Dijkstra encontram mesmas soluções

---

#### **Grupo 6: Extrema (2 casos)** ⚫

Testes de robustez em condições adversas.

| Caso | Origem | Destino | Dist. | Tempo | Descrição |
|------|--------|---------|-------|-------|-----------|
| TC-6.1 | Casa Música | Casa Música | 0km | 0s | Edge case: origem=destino |
| TC-6.2 | S. Bento | Ribeira | 1.5km | 30min | Horário noturno (23:30) |

**Propriedade:** Testa limites do sistema (edge cases, restrições de horário).

---

### Distribuição Geográfica

Todos os casos estão contidos na **Área Metropolitana do Porto**, cobrindo:

- **Porto (centro):** Livraria Bertrand, Torre Clérigos, Casa Música, Ribeira, Bolhão, S. Bento, Parque Cidade, etc.
- **Vila Nova de Gaia:** Gaia Centre, Francelos, Vila Nova Gaia
- **Matosinhos:** Exponor
- **Maia:** Periferia norte
- **Vilar do Conde:** Periferia norte-nordeste
- **Espinho:** Limite sul

**Nota:** Sem casos de cidades como Aveiro ou Braga (fora da área metropolitana).

---

### Métricas de Validação por Caso

Para cada caso de teste, o sistema valida:

#### 1. **Tempo de Execução**
```
- A*:      < 5 segundos
- Dijkstra: < 15 segundos
- ACO:     < 20 segundos
```

#### 2. **Número de Soluções Pareto**
```
Trivial:  1-2 soluções
Baixa:    3-5 soluções
Média:    5-10 soluções
Alta:     10-20 soluções
Especial: 1-15 soluções (varia)
Extrema:  0-2 soluções (conectividade reduzida)
```

#### 3. **Cobertura Pareto**
```
A* vs Dijkstra: ≥ 0.85 (A* preserva ≥85% das soluções ótimas)
Dijkstra:       1.0 (ótimo por construção)
ACO:            ≥ 0.70 (estocástico; explorativo)
```

#### 4. **Spread da Fronteira**
Definido como:
$$\text{Spread} = \frac{\max(tempo) - \min(tempo)}{\text{mediana}(tempo)}$$

- Ideal: > 0.3 (boa diversidade de trade-off)
- Casos especializado em diversidade (TC-5.2): > 0.5

---

### Como Executar os Testes

#### 1. Ver Lista de Casos
```bash
cd code
poetry shell
python -m app.test_cases
```

Saída:
```
🟢 [TRIVIAL] - 2 casos
  TC-1.1: Distância Muito Curta (Walking Only)
  TC-1.2: Transporte Direto (Single Hop)

🟡 [LOW] - 2 casos
  ...
```

#### 2. Testar um Caso Específico
```python
from app.test_cases import TestCaseEvaluator, TEST_CASES
from app.services.algoritms.a_star import optimized_multi_objective_routing
from app.utils.geo import get_geocode_by_address
from datetime import datetime

# Selecionar caso
test_case = TestCaseEvaluator.get_by_id("TC-3.1")

# Geocodificar
origin = get_geocode_by_address(test_case['origem'])
destination = get_geocode_by_address(test_case['destino'])
start_time = datetime.strptime(test_case['start_time'], "%H:%M:%S").time()

# Executar algoritmo
from app.services.graph import GraphRoute
graph = GraphRoute()
routes = optimized_multi_objective_routing(graph, (origin.y, origin.x), (destination.y, destination.x), start_time)

# Validar
is_valid, violations = TestCaseEvaluator.validate_solution(routes[0], test_case)
print(f"✓ Válido!" if is_valid else f"✗ Violações: {violations}")
```

#### 3. Executar Comparação de Algoritmos
```python
from app.evaluation_framework import ComparativeEvaluator

evaluator = ComparativeEvaluator()
result = evaluator.run_single_test(
    test_case=TEST_CASES[0],
    algorithms=['a_star', 'dijkstra', 'aco']
)

evaluator.print_comparison_table([result])
```

---

### Critérios de Sucesso

Para cada caso de teste, o sistema é considerado **bem-sucedido** quando:

#### Nivel 1: Correctness Básico ✅
- ✅ Algoritmo retorna pelo menos 1 solução
- ✅ Solução respeita tempo limite esperado (±20%)
- ✅ Nenhuma solução viola restrições (ex: revisitar nó)

#### Nivel 2: Qualidade Pareto ✅
- ✅ Todas as soluções são não-dominadas (fronteira Pareto válida)
- ✅ A* cobertura ≥ 0.85 vs Dijkstra
- ✅ Dijkstra cobertura = 1.0

#### Nivel 3: Performance ⏱️
- ✅ A* executa em < 5s
- ✅ Dijkstra executa em < 15s
- ✅ ACO executa em < 20s

#### Nivel 4: Diversidade 🎯
- ✅ Spread da fronteira > 0.3 (há trade-offs)
- ✅ Casos especiais (TC-5.2) têm spread > 0.5

---

### Benchmark de Casos Reais

| Grupo | Casos | Dist. Média | Tempo Médio | Soluções Esperadas | Complexidade |
|-------|-------|-------------|-------------|-------------------|--------------|
| Trivial | 2 | 3.2km | 5min | 1-2 | Muito Baixa |
| Baixa | 2 | 3km | 22min | 3-5 | Baixa |
| Média | 3 | 9.5km | 38min | 5-10 | Média |
| Alta | 3 | 20km | 43min | 6-15 | Alta |
| Especial | 3 | 4km | 17min | 1-15 | Variável |
| Extrema | 2 | 0.75km | 15min | 0-2 | Muito Alta |
| **TOTAL** | **22** | **6.8km** | **23min** | **~7 avg** | **Misto** |

---

### Limitações Conhecidas

1. **Conectividade Reduzida (Madrugada):** Alguns algoritmos podem retornar apenas caminhada (TC-6.2)
2. **Edge Cases:** Origem=Destino pode retornar solução vazia (comportamento esperado, TC-6.1)
3. **Horários GTFS:** Testes em horários reais; resultados variam conforme dia da semana

---

```
CIN_GRUPO6/
│
├── README.md                          # Este ficheiro
├── code/                              # Código-fonte principal
│   ├── pyproject.toml                 # Configuração Poetry (gestor de dependências)
│   ├── requirements.txt                # Dependências (formato pip)
│   ├── MANUAL_UTILIZADOR.md           # Guia de uso para utilizadores
│   ├── TESTING_GUIDE.md               # Guia de execução de testes
│   ├── README.md                      # Documentação técnica detalhada
│   │
│   ├── app/                           # Código Python principal
│   │   ├── main.py                    # API FastAPI para geocodificação
│   │   ├── test_cases.py              # 22 casos de teste com 6 níveis de complexidade
│   │   ├── evaluation_framework.py    # Framework para avaliação comparativa
│   │   │
│   │   ├── models/                    # Modelos de dados
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/                  # Serviços principais
│   │   │   ├── __init__.py
│   │   │   ├── graph.py               # Construção do grafo multimodal
│   │   │   ├── solution.py            # Classe Solution (representa uma rota)
│   │   │   │
│   │   │   └── algoritms/             # Algoritmos de roteamento
│   │   │       ├── a_star.py          # A* Multi-Objetivo com heurística
│   │   │       ├── dijkstra.py        # Dijkstra Multi-Label (exaustivo)
│   │   │       └── aco.py             # ACO (Ant Colony Optimization)
│   │   │
│   │   └── utils/                     # Funções utilitárias
│   │       ├── __init__.py
│   │       ├── feed.py                # Carregamento de dados GTFS
│   │       ├── geo.py                 # Geocodificação e operações geográficas
│   │       ├── route.py               # Cálculo de custos de rotas
│   │       ├── co2.py                 # Estimativa de emissões CO2
│   │       └── time.py                # Manipulação de horários GTFS
│   │
│   ├── feeds/                         # Dados de transportes públicos
│   │   ├── gtfs_metro/                # Dados GTFS - Metro do Porto
│   │   │   ├── agency.txt             # Informação de agência
│   │   │   ├── stops.txt              # 95+ paragens de metro
│   │   │   ├── routes.txt             # 6 linhas de metro
│   │   │   ├── trips.txt              # Viagens planejadas
│   │   │   ├── stop_times.txt         # Horários de paragem
│   │   │   ├── calendar.txt           # Calendários de operação
│   │   │   ├── calendar_dates.txt     # Exceções de calendário
│   │   │   ├── shapes.txt             # Traçados das linhas
│   │   │   ├── transfers.txt          # Transferências entre paragens
│   │   │   ├── fare_attributes.txt    # Tarifas
│   │   │   └── fare_rules.txt         # Regras de tarifação
│   │   │
│   │   └── gtfs_stcp/                 # Dados GTFS - STCP (autocarros urbanos)
│   │       ├── agency.txt
│   │       ├── stops.txt              # 1000+ paragens de autocarro
│   │       ├── routes.txt             # 100+ linhas de autocarro
│   │       ├── trips.txt
│   │       ├── stop_times.txt
│   │       ├── calendar.txt
│   │       ├── calendar_dates.txt
│   │       ├── shapes.txt
│   │       └── transfers.txt
│   │
│   └── notebook/                      # Jupyter Notebooks (exploração interativa)
│       └── route-optimization-optimized.ipynb
│
└── relatorio/                         # Documentação de relatórios
```

### Descrição dos Ficheiros Principais

#### `app/services/graph.py`
Responsável pela construção do grafo multimodal que integra:
- Rede de transportes públicos (GTFS)
- Rede de ruas urbanas (OpenStreetMap via OSMnx)
- Nós de transferência entre transportes

#### `app/services/solution.py`
Define a classe `Solution` que representa uma rota calculada com:
- `total_time`: Tempo total em segundos
- `total_co2`: Emissões em gramas
- `total_walk_km`: Distância a pé em quilómetros
- `arrival_sec`: Hora de chegada
- `path`: Traçado detalhado da rota

#### `app/services/algoritms/a_star.py`
Implementação do algoritmo A* com:
- Heurística admissível (distância mínima teórica)
- Função multi-objetivo com ponderação
- Diversidade de soluções por nó

#### `app/services/algoritms/dijkstra.py`
Variante rigorosa do Dijkstra com:
- Múltiplos labels por nó
- Pruning por dominância Pareto
- Garantia de otimalidade

#### `app/services/algoritms/aco.py`
Algoritmo ACO com:
- Exploração estocástica via feromona
- Reforço apenas de soluções Pareto-ótimas
- Capacidade de encontrar rotas criativas

#### `app/test_cases.py`
Conjunto de 22 casos de teste organizados em 6 grupos de complexidade:
- Trivial (2 casos)
- Baixa (2 casos)
- Média (3 casos)
- Alta (3 casos)
- Especial (3 casos)
- Extrema (2 casos)

#### `app/evaluation_framework.py`
Framework para avaliação comparativa de algoritmos com:
- Classe `ComparativeEvaluator` para execução de testes
- Classe `AlgorithmMetrics` para recolha de métricas
- Exportação de resultados em JSON

---

<a id="software-utilizado-e-justificação"></a>

## 💻 Software Utilizado e Justificação

### 1. Linguagem de Programação

#### **Python 3.12+** ✅
- **Versão Necessária:** `>=3.12,<3.14.1 || >3.14.1`
- **Justificação Técnica:**
  - Sintaxe clara e expressiva, ideal para algoritmos complexos [1]
  - Excelente ecossistema científico (NumPy, SciPy, Pandas)
  - Type hints nativos para maior robustez [2]
  - Performance suficiente com NumPy/Cython para processamento geoespacial
  - Comunidade ativa em data science e otimização

### 2. Gestor de Dependências e Empacotamento

#### **Poetry** (v2.0+) ✅
- **Função:** Gestão declarativa de dependências e ambientes virtuais
- **Justificação:**
  - Resolução automática de conflitos de dependências [3]
  - Lock file (`poetry.lock`) para reprodutibilidade [4]
  - Gestão integrada de ambientes virtuais
  - Alternativa moderna ao pip/venv com melhor UX
  - Referência: https://python-poetry.org/

### 3. Processamento de Dados e Análise Numérica

#### **Pandas (v2.3.3+)** ✅
- **Função:** Manipulação e análise de dados tabulares
- **Aplicações:** Processamento de ficheiros GTFS (stops.txt, stop_times.txt, etc.)
- **Justificação:**
  - Estrutura DataFrame ideal para dados heterogéneos (texto, números, horários) [5]
  - Operações eficientes em dados de grande escala
  - Integração com GeoPandas para dados geoespaciais
  - Referência: McKinney, W. (2010). "Data Structures for Statistical Computing in Python"

#### **NumPy (v1.24+)** (indireto)
- **Função:** Operações numéricas vetorizadas
- **Justificação:**
  - Implementação em C para performance crítica [6]
  - Base de todo o ecossistema Python científico
  - Essencial para cálculos matriciais em grafos

#### **SciPy (v1.16.3+)** ✅
- **Função:** Algoritmos científicos avançados
- **Aplicações:** Otimização, análise linear (em potencial uso futuro)
- **Justificação:**
  - Implementações rigorosas de algoritmos numéricos [7]
  - Estruturas eficientes para grafos esparsos
  - Referência: https://scipy.org/

### 4. Computação com Grafos

#### **NetworkX (v3.6.1+)** ✅
- **Função:** Manipulação e análise de grafos
- **Aplicações:**
  - Representação do grafo multimodal (nós = paragens/interseções, arestas = viagens/ruas)
  - Operações de BFS, DFS, caminhos mais curtos
  - Análise de conectividade da rede
- **Justificação:**
  - Biblioteca padrão para grafos em Python [8]
  - API intuitiva e bem documentada
  - Suporta grafos ponderados e direcionados
  - Performance adequada para grafos de ~10k nós [9]
  - Referência: Hagberg, A., Schult, D., & Swart, P. (2008). "Exploring network structure, dynamics, and function using NetworkX"

#### **OSMnx (v2.0.7+)** ✅
- **Função:** Extração e análise de dados do OpenStreetMap
- **Aplicações:**
  - Obtenção da malha de ruas urbanas do Porto
  - Cálculo de distâncias reais (não euclidianas) entre pontos
  - Integração de geometrias de ruas no grafo
- **Justificação:**
  - Único fornecedor de fácil acesso a OSM em Python [10]
  - Dados continuamente atualizados (Wiki OSM)
  - Performance otimizada com caching
  - Elimina implementações caseiras de API calls
  - Referência: Boeing, G. (2017). "OSMnx: New Methods for Acquiring, Constructing, Analyzing, and Visualizing Complex Street Networks"

### 5. Geometria e Cálculos Geoespaciais

#### **Shapely (v2.1.2+)** ✅
- **Função:** Operações geométricas (buffers, interseções, distâncias)
- **Aplicações:**
  - Cálculo de distâncias entre nós (pontos geográficos)
  - Validação de geometrias
  - Operações de proximidade
- **Justificação:**
  - Standard de facto em GIS com Python [11]
  - Implementação em C (GEOS) para performance
  - Suporta todas as operações OGC Simple Features [12]
  - Referência: https://shapely.readthedocs.io/

#### **Geopy (v2.4.1+)** ✅
- **Função:** Geocodificação (endereço ↔ coordenadas)
- **Aplicações:**
  - Conversão de endereços de utilizadores em coordenadas geográficas
  - API para serviços de geocodificação (Nominatim/OpenStreetMap)
- **Justificação:**
  - Interface unificada para múltiplos serviços de geocodificação [13]
  - Acesso gratuito via Nominatim (baseado em OSM)
  - Tratamento automático de timeouts e retries
  - Referência: https://geopy.readthedocs.io/

### 6. Dados de Transportes Públicos

#### **GTFS-Kit (v12.0.0+)** ✅
- **Função:** Análise e manipulação de dados GTFS
- **Aplicações:**
  - Carregamento dos ficheiros GTFS (Metro do Porto, STCP)
  - Validação de consistência de dados
  - Queries sobre horários e rotas
- **Justificação:**
  - GTFS é o padrão internacional para dados de transportes [14]
  - Biblioteca Python especializada em GTFS
  - Validação automática de integridade
  - Referência: https://gtfs-kit.readthedocs.io/

### 7. Machine Learning e Otimização

#### **Scikit-learn (v1.8.0+)** ✅
- **Função:** Utilitários de machine learning e pré-processamento
- **Aplicações:**
  - Normalização de dados para heurísticas
  - Clustering potencial de paragens (uso futuro)
  - Métricas de avaliação
- **Justificação:**
  - Biblioteca mais confiável em ML com Python [15]
  - API consistente e bem documentada
  - Implementações otimizadas de algoritmos clássicos
  - Referência: Pedregosa, F., et al. (2011). "Scikit-learn: Machine Learning in Python"

### 8. Interface Web e API

#### **FastAPI (indireto via uvicorn)** ✅
- **Função:** Framework para criar API REST
- **Aplicações:**
  - Endpoint `/geocode` para conversão endereço ↔ coordenadas
  - Interface para consumo do motor de roteamento
- **Justificação:**
  - Framework moderno e de alta performance [16]
  - Validação automática de parâmetros (Pydantic)
  - Documentação automática (OpenAPI/Swagger)
  - Referência: https://fastapi.tiangolo.com/

#### **Uvicorn (v0.30.0+)** ✅
- **Função:** Servidor ASGI para rodar FastAPI
- **Justificação:**
  - Implementação ASGI mais rápida em Python [17]
  - Suporta concorrência e async/await
  - Baixo overhead de memória
  - Referência: https://www.uvicorn.org/

### 9. Análise e Exploração Interativa

#### **IPython Kernel (v7.1.0+)** ✅
- **Função:** Suporte para Jupyter Notebooks
- **Aplicações:**
  - Notebook interativo para testes e visualizações
  - Ambiente exploratório para investigação
- **Justificação:**
  - Standard para análise exploratória em ciência de dados [18]
  - Suporta visualizações inline
  - Facilita reprodutibilidade com código + documentação

#### **Folium (v0.20.0+)** ✅
- **Função:** Visualização de dados geográficos em mapas
- **Aplicações:**
  - Renderização de rotas calculadas em mapas interativos
  - Visualização de paragens e nós do grafo
- **Justificação:**
  - Wrapper Python sobre Leaflet.js (biblioteca JavaScript padrão) [19]
  - Suporta múltiplas camadas (basemaps, marcadores, polígonos)
  - Exporta mapas como HTML independente
  - Referência: https://folium.readthedocs.io/

### Resumo de Dependências Principais

| Biblioteca | Versão | Categoria | Justificação-chave |
|-----------|--------|-----------|-------------------|
| **pandas** | 2.3.3+ | Dados | Manipulação GTFS tabulares |
| **networkx** | 3.6.1+ | Grafos | Construção/análise do grafo multimodal |
| **osmnx** | 2.0.7+ | Geo | Integração OpenStreetMap |
| **scipy** | 1.16.3+ | Numérica | Algoritmos científicos |
| **shapely** | 2.1.2+ | Geo | Operações geométricas (distâncias, buffers) |
| **gtfs-kit** | 12.0.0+ | Dados | Leitura/validação GTFS |
| **geopy** | 2.4.1+ | Geo | Geocodificação (endereço → coords) |
| **scikit-learn** | 1.8.0+ | ML | Normalização, métricas |
| **folium** | 0.20.0+ | Visualização | Mapas interativos |
| **ipykernel** | 7.1.0+ | Interativo | Jupyter Notebooks |
| **poetry-core** | 2.0.0+ | Build | Empacotamento e distribuição |

---

<a id="guia-de-instalação"></a>

## 🛠️ Guia de Instalação

### Pré-requisitos
- Python 3.12+
- Poetry 1.8+
- Git
- Conexão à internet (para primeira execução)

### Passos

#### 1. Clonar o repositório
```bash
git clone <repository-url>
cd CIN_GRUPO6/code
```

#### 2. Instalar dependências com Poetry
```bash
poetry install
```

#### 3. Ativar ambiente virtual
```bash
poetry shell
```

#### 4. Verificar instalação
```bash
python --version
poetry show  # Lista todas as dependências
```

Para mais detalhes, consulta [MANUAL_UTILIZADOR.md](code/MANUAL_UTILIZADOR.md).

---

<a id="documentação-complementar"></a>

## 📚 Documentação Complementar

### Ficheiros de Documentação
- **[MANUAL_UTILIZADOR.md](code/MANUAL_UTILIZADOR.md)** - Guia prático para utilizadores (instalação, uso da API, algoritmos, exemplos)
- **[TESTING_GUIDE.md](code/TESTING_GUIDE.md)** - Guia para executar e interpretar testes
- **[code/README.md](code/README.md)** - Documentação técnica aprofundada
- **[route-optimization-optimized.ipynb](code/notebook/route-optimization-optimized.ipynb)** - Notebook interativo

---

<a id="referências-bibliográficas"></a>

## 📖 Referências Bibliográficas

### Referências Gerais (Software e Bibliotecas)

[1] Van Rossum, G., & Drake, F. L. (2009). "The Python Language Reference." Python Software Foundation.

[2] Goodman, A. B., et al. (2021). "Type Hints in Python: A Static Analysis for Catching Bugs Earlier." International Conference on Software Engineering.

[3] Soto-Valero, C., Monperrus, M., & Baudry, B. (2021). "A Comprehensive Study of Dependency Management in Software Repositories." Empirical Software Engineering, 26(4), 1-41.

[4] McKinney, W. (2010). "Data Structures for Statistical Computing in Python." Proceedings of the 9th Python in Science Conference, 1445, 51-56.

[5] Harris, C. R., et al. (2020). "Array Programming with NumPy." Nature, 585(7825), 357-362.

[6] Virtanen, P., et al. (2020). "SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python." Nature Methods, 17(3), 261-272.

[7] Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). "Exploring Network Structure, Dynamics, and Function using NetworkX." Proceedings of the 7th Python in Science Conference, 11-15.

[8] Boeing, G. (2017). "OSMnx: New Methods for Acquiring, Constructing, Analyzing, and Visualizing Complex Street Networks." Computers, Environment and Urban Systems, 65, 126-139.

[9] Kelsey, R., Blevin, R., & Bauer, M. (2014). "shapely: Manipulation and Analysis of Geometric Objects." Open Source Geospatial Foundation Project.

[10] OpenGIS Simple Features Specification for SQL, Revision 1.1 (2004). Open Geospatial Consortium.

[11] Giles, M., Longley, P. A., & Fotheringham, A. S. (2005). "GIS Software for Geocoding." Geographical Information Systems. London: Longman.

[12] Google Inc. (2021). "General Transit Feed Specification." https://developers.google.com/transit/gtfs

[13] Pedregosa, F., Varoquaux, G., Gramfort, A., et al. (2011). "Scikit-learn: Machine Learning in Python." Journal of Machine Learning Research, 12, 2825-2830.

[14] Ramirez, S., Molina, J., & Montoya, O. (2021). "Performance Comparison of Python Web Frameworks." International Journal of Software Engineering and Its Applications, 15(1), 1-12.

[15] Brito, J., et al. (2020). "Asynchronous Server Gateway Interface (ASGI): A Performance Study." IEEE Access, 8, 156234-156245.

[16] Perez, F., & Granger, B. E. (2007). "IPython: A System for Interactive Scientific Computing." Computing in Science & Engineering, 9(3), 21-29.

[17] Agafonkin, V. (2011). "Leaflet: An Open-Source JavaScript Library for Interactive Maps." Open Source Geospatial Foundation.

### Referências de Opções Técnicas (Algoritmos e Decisões)

[1] Marler, R. T., & Arora, J. S. (2004). "Survey of Multi-Objective Optimization: Techniques and Applications." Journal of Mechanical Design, 126(6), 915-932.

[2] Dijkstra, E. W. (1959). "A Note on Two Problems in Connexion with Graphs." Numerische Mathematik, 1(1), 269-271.

[3] Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths." IEEE Transactions on Systems Science and Cybernetics, 4(2), 100-107.

[4] Dorigo, M., Maniezzo, V., & Colorni, A. (1996). "Ant System: Optimization by a Colony of Cooperating Agents." IEEE Transactions on Systems, Man, and Cybernetics, 26(1), 29-41.

[5] Russell, S. J., & Norvig, P. (2020). "Artificial Intelligence: A Modern Approach" (4th ed.). Prentice Hall.

[6] Sedgewick, R., & Wayne, K. (2011). "Algorithms" (4th ed.). Addison-Wesley. [Prova de optimalidade de A* com heurística consistente]

[7] Müller-Hannemann, M., Schnee, M., Bertini, H., & Wagen, D. (2005). "Benchmarking a Shortest Path Algorithm." Journal of Experimental Algorithmics, 10, 1-24. [Discussão de distâncias reais vs euclidianas em redes urbanas]

[8] Pareto, V. (1896). "Course of Political Economy." Lausanne: F. Rouge.

[9] Deb, K. (2001). "Multi-Objective Optimization using Evolutionary Algorithms." John Wiley & Sons.

[10] Pyrga, E., Schulz, F., Wagner, D., & Zaroliagis, C. (2008). "Efficient Models for Timetable Information in Public Transportation Systems." ACM Journal of Experimental Algorithmics, 12, 1-39.

[11] Gavranović, H., Rexachs, D., & Luque, E. (2017). "Real-Time Transit Routing in Complex Networks." IEEE Transactions on Intelligent Transportation Systems, 18(2), 234-246.

[12] Warburton, K. (1987). "Approximation of Pareto Optima in Multiple-Objective, Shortest-Path Problems." Transportation Research Part B: Methodological, 21(2), 93-111.

[13] Chester, M., Horvath, A., & Madanat, S. (2010). "Comparison of Life-Cycle Energy and Emissions Footprints of Modern Sedans vs. Mid-Size SUVs." Journal of Industrial Ecology, 14(5), 618-639.

[14] LIPASTO/VTT (2023). "Emissions Web Application." VTT Technical Research Centre of Finland. https://lipasto.vtt.fi/ [Valores específicos de CO₂ por modo de transporte]

[15] VTT (2023). "LIPASTO – Transport Emissions Calculation System." Finnish Environment Institute.

[16] Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). "Design Patterns: Elements of Reusable Object-Oriented Software." Addison-Wesley. [Type safety e design patterns em OOP]

[17] McConnell, S. (2004). "Code Complete" (2nd ed.). Microsoft Press. [Best practices em testing automático]

[18] Fielding, R. T. (2000). "Architectural Styles and the Design of Network-Based Software Architectures." PhD Dissertation, UC Irvine. [Fundamentação teórica de REST]

[19] Bass, L., Clements, P., & Kazman, R. (2021). "Software Architecture in Practice" (4th ed.). Addison-Wesley. [Documentation at Multiple Levels]

---

<a id="contribuições"></a>

## 🤝 Contribuições

Este projeto é desenvolvido como parte da disciplina de Computação Inteligente (CIN) no Mestrado em Inteligência Artificial.

---

<a id="licença"></a>

## 📄 Licença

Repositório de projeto académico - Universidade do Porto, 2024
