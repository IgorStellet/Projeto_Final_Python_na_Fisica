# Projeto Final — Python na Física (Caos + FOPT → GWs)

**Ideia geral.** Projeto final da disciplina “Python na Física” (CBPF): explorar **teoria do caos** em **mapas caóticos 
globalmente acoplados** e construir uma ponte conceitual com **ondas gravitacionais (GWs)** geradas por **transições de fase de primeira ordem (FOPTs)**. 
O objetivo desse projeto é conectar sua área de pesquisa, no meu caso FOPTs, com teoria do caos.
Ao longo da disciplina foram feitos 5 tarefas associando física estatística a python, desde o passeio aleatório ao modelo 
de ising e teoria dos jogos. Coloco também essas tarefas aqui nesse repositório.

**Artigo principal:** *Synchronization and phase ordering in globally coupled chaotic maps* (Alvarez-Llamoza & Cosenza, 2014).  
**Artigo de apoio:** *First-order Synchronization Transition in Locally Coupled Maps* (Mohanty, 2004).

## Objetivos do projeto
- Reproduzir e comentar as **fronteiras de sincronização** (Fig. 1), **persistência** e **ordem de fase antes da sincronização completa** (Figs. 2–3),
e **distribuições/séries temporais** (Figs. 4–5).
- Conectar os resultados com FOPT→GWs (colisões de paredes, ondas sonoras, sensibilidade às condições iniciais).

## Instalação rápida (local)
Requer **Python ≥ 3.11**.
```bash
git clone https://github.com/IgorStellet/Projeto_Final_Python_na_Fisica.git
cd Projeto_Final_Python_na_Fisica
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .[dev]
```
