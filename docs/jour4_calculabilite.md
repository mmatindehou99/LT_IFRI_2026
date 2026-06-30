# Jour 4 — Calculabilité : MT générique, MTU, calculatrice

**Modules :** `formlang/turing.py`, `formlang/utm.py`
**App :** `apps/calc/machines.py`, `apps/calc/calculator.py`
**Tests cibles :** `tests/test_turing.py`, `tests/test_calc.py`

## Objectifs

- MT déterministe générique (ruban `dict` bi-infini), avec **trace**.
- MTU : `encode(M)` (linéarisation JSON injective) → `decode` → simulation.
  Invariant clé : **U(⟨M⟩##w) == M(w)**.
- Calculatrice unaire : `+` et `-` sont de **vraies MT** ; `*` et `/` par
  **composition** (macro-machines).

## Tables (statut : tracées à la main)

- **ADD** `1ⁿ+1ᵐ → 1ⁿ⁺ᵐ` : le `+` devient `1` (fusion), puis on efface **un**
  `1` final. O(n+m).
- **SUB** `1ⁿ-1ᵐ → 1ⁿ⁻ᵐ` (n ≥ m) : appariement par marquage `X` (n barré de
  **droite à gauche** ⇒ survivants contigus, sortie propre), puis nettoyage.
  O(n·m).
- **MUL / DIV** : addition / soustraction répétées via les MT primitives.

## Théorie à rédiger

- Définition de la MTU ; **encodage** ⟨M⟩##w (injectif, décodable).
- **Surcoût** de simulation : à **sourcer** (multi-ruban O(t·|⟨M⟩|) ;
  Hennie–Stearns pour le facteur logarithmique). *Ne pas inventer de constante
  — vérifier le cours / Sipser avant de l'écrire comme un fait.*
- **Indécidabilité de l'arrêt** : « U s'arrête sur ⟨M⟩##w » est indécidable
  (diagonalisation). L'universalité n'est pas l'omniscience.

## Critère de fin de journée

`pytest tests/test_turing.py tests/test_calc.py -q` au vert (calc exhaustif
sur 0..6 pour +, −, ×, ÷ ; round-trip d'encodage ; U == M).

