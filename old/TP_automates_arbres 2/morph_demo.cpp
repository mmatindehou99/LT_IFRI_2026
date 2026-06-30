// morph_demo.cpp — de la SURFACE à l'ARBRE, validé par l'automate (Exercice 4).
//
// Chaîne complète, AUTONOME :
//   (1) découverte de morceaux d'affixes par une heuristique CLASSIQUE d'alternance
//       (un affixe alterne avec ∅ : X et X+suf — resp. pre+X — tous deux attestés ;
//        idée de Z. Harris, 1955). Texte d'entrée brut, aucune annotation.
//   (2) segmentation gloutonne de chaque mot en (préfixes*, racine, suffixes*) ;
//   (3) construction de l'ARBRE, puis VALIDATION + CLASSIFICATION par l'automate
//       d'arbres (tree_automaton.hpp) — c'est le cœur du TP.
//
// NB : entrée supposée en ASCII (corpus du TP). Pour de l'Unicode, segmenter par
//      points de code — laissé en exercice.
//
// Usage : ./morph_demo corpus_A_prefixing.txt corpus_B_suffixing.txt

#include "tree_automaton.hpp"

#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

using namespace ta;

// (1) Découverte — heuristique d'alternance avec ∅, sur ≥ K racines attestées.
static std::set<std::string> discover(const std::set<std::string>& vocab, bool prefix_side, int K = 3) {
    std::map<std::string, std::set<std::string>> alt;
    for (const auto& w : vocab)
        for (int n = 1; n <= 3; ++n) {
            if ((int)w.size() <= n + 1) continue;
            std::string affix = prefix_side ? w.substr(0, n) : w.substr(w.size() - n);
            std::string stem  = prefix_side ? w.substr(n)    : w.substr(0, w.size() - n);
            if (vocab.count(stem)) alt[affix].insert(stem);
        }
    std::set<std::string> out;
    for (auto& [a, roots] : alt) if ((int)roots.size() >= K) out.insert(a);
    return out;
}

// (2) Segmentation gloutonne avec les affixes découverts.
static TreePtr segment_to_tree(std::string w,
                               const std::set<std::string>& PRE,
                               const std::set<std::string>& SUF) {
    std::vector<std::string> pres, sufs;
    // préfixes : retirer en tête tant qu'on reconnaît un préfixe (et qu'il reste ≥2)
    bool changed = true;
    while (changed) {
        changed = false;
        for (int n = 3; n >= 1; --n)
            if ((int)w.size() > n + 1 && PRE.count(w.substr(0, n))) {
                pres.push_back(w.substr(0, n)); w = w.substr(n); changed = true; break;
            }
    }
    // suffixes : retirer en queue tant qu'on reconnaît un suffixe (et qu'il reste ≥2)
    changed = true; std::vector<std::string> rev_sufs;
    while (changed) {
        changed = false;
        for (int n = 3; n >= 1; --n)
            if ((int)w.size() > n + 1 && SUF.count(w.substr(w.size() - n))) {
                rev_sufs.push_back(w.substr(w.size() - n)); w = w.substr(0, w.size() - n); changed = true; break;
            }
    }
    for (auto it = rev_sufs.rbegin(); it != rev_sufs.rend(); ++it) sufs.push_back(*it);

    // (3) construire l'arbre word(prefixes…, rest(root, suffixes…))
    TreePtr pchain = nil();
    for (auto it = pres.rbegin(); it != pres.rend(); ++it) pchain = prefixes(prefix(*it), pchain);
    TreePtr schain = nil();
    for (auto it = sufs.rbegin(); it != sufs.rend(); ++it) schain = suffixes(suffix(*it), schain);
    return word(pchain, rest(root(w), schain));
}

int main(int argc, char** argv) {
    if (argc < 2) { std::cerr << "usage: " << argv[0] << " <wordlist.txt> [autres...]\n"; return 1; }
    TreeAutomaton A;
    for (int a = 1; a < argc; ++a) {
        std::ifstream in(argv[a]);
        if (!in) { std::cerr << "  (illisible: " << argv[a] << ")\n"; continue; }
        std::set<std::string> vocab; std::string line, w;
        while (std::getline(in, line)) { std::istringstream ss(line); while (ss >> w) vocab.insert(w); }

        auto PRE = discover(vocab, /*prefix_side=*/true);
        auto SUF = discover(vocab, /*prefix_side=*/false);

        std::map<Class, int> count;
        for (const auto& word_ : vocab) count[classify(A, segment_to_tree(word_, PRE, SUF))]++;

        std::cout << "== " << argv[a] << " ==  (" << vocab.size() << " formes)\n";
        std::cout << "  affixes découverts : " << PRE.size() << " préfixe(s), "
                  << SUF.size() << " suffixe(s)\n";
        std::cout << "  classes (via l'automate) :";
        for (Class c : {Class::Bare, Class::Prefixed, Class::Suffixed, Class::Circumfixed, Class::Invalid})
            std::cout << "  " << class_name(c) << "=" << count[c];
        std::cout << "\n\n";
    }
    std::cout << "L'automate d'arbres a VALIDÉ puis CLASSÉ chaque mot segmenté.\n";
    return 0;
}
