# formlang — De l'automate fini à la machine universelle

Projet intégrateur d'une semaine (Master GL, IFRI — Théorie des langages &
calculabilité). Une **seule** bibliothèque (`formlang/`) gravit la hiérarchie de
Chomsky ; deux études de cas (`apps/`) la réutilisent ; un pipeline l'enchaîne.

> **Règle d'or :** les `apps/` n'ont **pas le droit** de redéfinir un automate —
> elles instancient ceux de `formlang/`. C'est ce qui fait l'unité du projet.

## Carte du projet

| Couche `formlang` | Pouvoir | Module |
|---|---|---|
| AFD / AFN | régulier | `dfa.py`, `nfa.py` |
| transducteur | rationnel | `fst.py` |
| pile / grammaire | hors-contexte | `pda.py`, `cfg.py` |
| automate d'arbres | arbres réguliers | `tree.py` |
| MT / MTU | récursivement énumérable | `turing.py`, `utm.py` |
| Myhill–Nerode | transversal | `myhill_nerode.py` |

| Étude de cas (`apps/`) | Réutilise | But |
|---|---|---|
| `morpho/` | `tree` | segmenter + classer (BARE/PREFIXED/SUFFIXED/CIRCUMFIXED) |
| `shield/` | `dfa`, `fst`, `pda`, `tree` | défense 100 % structurelle (jetons abstraits) |
| `calc/` | `turing`, `utm` | calculatrice unaire exécutée par la machine universelle |

## Démarrage

```bash
python setup_projet.py        # (option 2) crée l'arborescence + fichiers
pip install pytest
pytest -q                     # tout doit virer au vert
python pipeline.py            # démo Shield
python pipeline.py --word 4or
python pipeline.py --morpho mufafak
```

## Cadre éthique (volet Shield)

100 % structurel. Un prompt = suite de **jetons abstraits**
`{a, o, r, e, [, ], (, )}`. Aucune attaque réelle, aucun contenu sensible. On
enseigne à *reconnaître une structure de défense* — sécurité défensive. Tout
rendu contenant un exemple d'attaque réelle est hors-sujet et pénalisé.

## Statut de vérification

- Tables `ADD`/`SUB` (calculatrice) et logique du BUTA : **tracées à la main**.
- Tout le reste : **garanti par `pytest`** — c'est la suite de tests qui fait foi.
- Toute borne de complexité dans le rapport doit être **démontrée ou sourcée**
  (pas de constante « de mémoire »).

## Licence

Domaine public (CC0) — matériel pédagogique.

