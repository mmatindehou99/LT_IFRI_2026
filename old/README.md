# Matériel pédagogique — TP Théorie des langages / LLM-Secure Shield

Ressources pour un TP de **Master Génie Logiciel (IFRI)** illustrant la théorie des
langages (expressions régulières, automates finis, transducteurs, grammaires,
automates à pile, **automates d'arbres**) à partir des méthodes **défensives** du
moteur **LLM-Secure Shield**.

> **Cadre éthique.** 100 % structurel. Tous les *prompts* sont des suites de **jetons
> abstraits** (`a, o, r, e, [, ], (, )`). Aucune attaque réelle, aucun contenu sensible.
> On enseigne à **reconnaître des structures** — c'est de la sécurité défensive.

## Fichiers

| Fichier | Public | Contenu |
|---|---|---|
| `TP_Shield_Theorie_des_Langages.md` | Étudiants | Énoncé complet + barème (20 + 2 bonus) |
| `CORRIGE_TP_Shield.md` | Enseignant | Corrigé détaillé, notes de correction |
| `squelette_tp_shield.py` | Étudiants | Code à compléter (tests fournis) |
| `corrige_tp_shield.py` | Enseignant | Solution de référence (tests verts) |

## Correspondance méthodes du Shield ↔ théorie des langages

| Partie | Méthode du Shield | Outil formel |
|---|---|---|
| 1 | `SingularityDetector` | Expressions régulières / AFD |
| 2 | `EnhancedNormalizer` | Transducteur fini |
| 3 | Détection de délimiteurs | Grammaire hors-contexte / automate à pile |
| 4 | `AttackDecomposer` | **Automate d'arbres ascendant** (cœur du TP) |
| 5 | `CongruenceClassifier` | Congruence de Myhill-Nerode / minimisation |

## Lancer les tests

```bash
python3 corrige_tp_shield.py   # solution de référence : tout doit être vert
python3 squelette_tp_shield.py # côté étudiant : échoue tant que non complété
```

Aucune dépendance externe (Python 3 standard).
