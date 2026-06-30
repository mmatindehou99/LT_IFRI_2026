// tree_automaton.hpp — Automate d'arbres ASCENDANT (bottom-up) pour la morphologie.
//
// Outil pédagogique AUTONOME (TP « Théorie des langages »). Aucune dépendance
// externe : uniquement la bibliothèque standard C++17. Domaine public (CC0) — voir
// LICENSE. Écrit pour le TP ; construction standard d'automate d'arbres.
//
// Rappel théorique (cf. énoncé §2) — un automate d'arbres ascendant déterministe
//   A = (Q, Σ, Q_f, Δ)
// reconnaît un ARBRE en remontant des feuilles vers la racine : chaque nœud reçoit
// un état calculé à partir des états de ses enfants par une règle f(q1,…,qn) → q.
// L'arbre est accepté ssi la racine reçoit un état final.

#pragma once

#include <map>
#include <memory>
#include <set>
#include <string>
#include <utility>
#include <vector>

namespace ta {

// ---------------------------------------------------------------------------
// Alphabet rangé Σ : symboles internes (arité 2) et feuilles (arité 0).
//   word(prefixes, rest) | rest(root, suffixes)
//   prefixes(prefix, prefixes|nil) | suffixes(suffix, suffixes|nil)
// ---------------------------------------------------------------------------
enum class Kind {
    Word, Rest, Prefixes, Suffixes,   // internes, arité 2
    Prefix, Root, Suffix, Nil         // feuilles, arité 0
};

struct Tree {
    Kind kind;
    std::string label;                            // texte du morphème (feuilles)
    std::vector<std::shared_ptr<Tree>> kids;
};
using TreePtr = std::shared_ptr<Tree>;

// --- constructeurs lisibles ------------------------------------------------
inline TreePtr leaf(Kind k, std::string s = "") {
    auto t = std::make_shared<Tree>(); t->kind = k; t->label = std::move(s); return t;
}
inline TreePtr inner(Kind k, TreePtr a, TreePtr b) {
    auto t = std::make_shared<Tree>(); t->kind = k; t->kids = {std::move(a), std::move(b)}; return t;
}
inline TreePtr prefix(std::string s) { return leaf(Kind::Prefix, std::move(s)); }
inline TreePtr root  (std::string s) { return leaf(Kind::Root,   std::move(s)); }
inline TreePtr suffix(std::string s) { return leaf(Kind::Suffix, std::move(s)); }
inline TreePtr nil()                 { return leaf(Kind::Nil); }
inline TreePtr prefixes(TreePtr h, TreePtr t) { return inner(Kind::Prefixes, std::move(h), std::move(t)); }
inline TreePtr suffixes(TreePtr h, TreePtr t) { return inner(Kind::Suffixes, std::move(h), std::move(t)); }
inline TreePtr rest(TreePtr r, TreePtr s)     { return inner(Kind::Rest, std::move(r), std::move(s)); }
inline TreePtr word(TreePtr p, TreePtr r)     { return inner(Kind::Word, std::move(p), std::move(r)); }

// frontière (yield) : concaténation des feuilles non-nil, de gauche à droite.
inline std::string yield(const TreePtr& t) {
    if (!t) return "";
    if (t->kids.empty()) return t->kind == Kind::Nil ? "" : t->label;
    std::string s; for (const auto& k : t->kids) s += yield(k); return s;
}

// ---------------------------------------------------------------------------
// Automate d'arbres ascendant déterministe.
// ---------------------------------------------------------------------------
using State = int;
constexpr State REJECT = -1;

class TreeAutomaton {
public:
    TreeAutomaton() { build_default_morphology(); }

    // Exécution ASCENDANTE. Renvoie l'état de la racine, ou REJECT. Coût O(|arbre|).
    State run(const TreePtr& t) const {
        if (!t) return REJECT;
        std::vector<State> child_states;
        for (const auto& k : t->kids) {
            State s = run(k);
            if (s == REJECT) return REJECT;
            child_states.push_back(s);
        }
        auto it = delta_.find({t->kind, child_states});
        return it == delta_.end() ? REJECT : it->second;
    }

    bool accepts(const TreePtr& t) const { return final_.count(run(t)) > 0; }

    // API d'extension (Exercice 3.4) : ajouter règles / états finaux.
    void add_rule(Kind k, std::vector<State> children, State result) {
        delta_[{k, std::move(children)}] = result;
    }
    void add_final(State s) { final_.insert(s); }

    std::size_t num_rules() const { return delta_.size(); }

private:
    std::map<std::pair<Kind, std::vector<State>>, State> delta_;  // Δ : f(q…) → q
    std::set<State> final_;                                        // Q_f

    // États Q (un par catégorie syntaxique de l'arbre).
    enum : State { qPre = 1, qRoot, qSuf, qNil, qSufs, qPrefs, qRest, qWord };

    void build_default_morphology() {
        // feuilles
        add_rule(Kind::Prefix, {}, qPre);
        add_rule(Kind::Root,   {}, qRoot);
        add_rule(Kind::Suffix, {}, qSuf);
        add_rule(Kind::Nil,    {}, qNil);
        // chaîne de suffixes
        add_rule(Kind::Suffixes, {qSuf, qSufs}, qSufs);
        add_rule(Kind::Suffixes, {qSuf, qNil},  qSufs);
        // chaîne de préfixes
        add_rule(Kind::Prefixes, {qPre, qPrefs}, qPrefs);
        add_rule(Kind::Prefixes, {qPre, qNil},   qPrefs);
        // reste = racine + suffixes
        add_rule(Kind::Rest, {qRoot, qSufs}, qRest);
        add_rule(Kind::Rest, {qRoot, qNil},  qRest);
        // mot = préfixes + reste
        add_rule(Kind::Word, {qPrefs, qRest}, qWord);
        add_rule(Kind::Word, {qNil,   qRest}, qWord);   // mot sans préfixe
        // état final
        add_final(qWord);
    }
};

// ---------------------------------------------------------------------------
// Classification morphologique (lue sur un arbre VALIDÉ par l'automate).
// ---------------------------------------------------------------------------
enum class Class { Invalid, Bare, Suffixed, Prefixed, Circumfixed };

inline bool contains(const TreePtr& t, Kind k) {
    if (!t) return false;
    if (t->kind == k) return true;
    for (const auto& c : t->kids) if (contains(c, k)) return true;
    return false;
}

inline Class classify(const TreeAutomaton& A, const TreePtr& t) {
    if (!A.accepts(t)) return Class::Invalid;
    bool p = contains(t, Kind::Prefix), s = contains(t, Kind::Suffix);
    if (p && s) return Class::Circumfixed;
    if (s)      return Class::Suffixed;
    if (p)      return Class::Prefixed;
    return Class::Bare;
}

inline const char* class_name(Class c) {
    switch (c) {
        case Class::Invalid:     return "INVALID";
        case Class::Bare:        return "BARE";
        case Class::Suffixed:    return "SUFFIXED";
        case Class::Prefixed:    return "PREFIXED";
        case Class::Circumfixed: return "CIRCUMFIXED";
    }
    return "?";
}

}  // namespace ta
