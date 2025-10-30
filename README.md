# Projeto Final (Python na Física: Caos)
O projeto final da disciplina, python na Física, consiste em fazermos uma simulação envolvendo sua área de pesquisa e teoria do caos.

Durante o curos fizemos ao todo 5 tarefas envolvendo física estatística, do passeio aleatório ao modelo de ising e teoria dos jogos. Todas essas tarefas se encontraram aqui
na aba tarefas.

**Projeto final:** Sendo minha área de pesquisa first order phase transitions (FOPT's) que geram ondas gravitacionais (GW's), esse projeto terá como foco vizualizar o caos surgindo a partir de transições descontínuas, com as referências principais sendo: https://arxiv.org/abs/1402.4870 e secundariamente https://arxiv.org/abs/cond-mat/0402283.

Referência sobre FOPT: https://arxiv.org/abs/2305.02357. 

**Objetivo.** Reproduzir e extender os resultados chaves de *Alvarez‑Llamoza & Cosenza (2014)*, focando em **contornos sincronizados**, **ordem de fase antes da sincronização**, e **persistência**. Depois construir **ligações** como ondas gravitacionais (GW) geradas por transições de fase de primeira ordem (FOPTs).


> Main paper: **Synchronization and phase ordering in globally coupled chaotic maps** (2014).


## TL;DR — Quickstart


**Colab (recommended):** click the badge above. All notebooks live under `notebooks/`.


**Local install** (Python ≥ 3.11):
```bash
# clone
git clone https://github.com/IgorStellet/Projeto_Final_Python_na_Fisica.git
cd Projeto_Final_Python_na_Fisica


# create env (uv or pip)
python -m venv .venv && source .venv/bin/activate # Windows: .venv\\Scripts\\activate
pip install -U pip
pip install -e .[dev]
```
