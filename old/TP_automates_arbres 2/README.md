# TP — Automates d'arbres (Théorie des langages)

Paquet **autonome** et **domaine public** (CC0, voir `LICENSE`). Aucune dépendance
hors `g++` (C++17) et `python3`.

## Contenu

| Fichier | Rôle |
|---|---|
| `TP_automates_arbres.md` | **Énoncé** du TP (théorie + exercices + barème) |
| `CORRIGE.md` | Corrigé enseignant (solutions + traces + barème détaillé) |
| `tree_automaton.hpp` | Automate d'arbres ascendant (en-tête autonome) |
| `ta_check.cpp` | Reconnaissance/classification d'arbres (Ex. 3) |
| `morph_demo.cpp` | Surface → arbre → automate sur corpus (Ex. 4) |
| `gen_corpora.py` | Génère deux mini-corpus synthétiques à vérité-terrain |
| `Makefile` | `make`, `make run`, `make corpora`, `make clean` |

## Démarrage rapide

```sh
make run        # compile tout, génère les corpus, exécute les deux démos
```

ou pas à pas :

```sh
make            # compile ta_check et morph_demo
make corpora    # génère corpus_A_prefixing.txt et corpus_B_suffixing.txt
./ta_check
./morph_demo corpus_A_prefixing.txt corpus_B_suffixing.txt
```

## Pré-requis (acquis du cours)

Langages formels, expressions régulières, grammaires, automates finis (AFD/AFN).
Le TP introduit les **automates d'arbres** comme généralisation des automates finis
des mots aux **arbres**.

## Pour l'enseignant

Distribuez aux étudiants tout SAUF `CORRIGE.md`. Le barème est en fin d'énoncé.
