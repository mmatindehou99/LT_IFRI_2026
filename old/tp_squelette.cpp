// =============================================================================
// TP — Automates d'arbres : reconnaissance morphologique (squelette étudiant)
// Théorie des langages — Master GL, IFRI
//
// Automate d'arbre ascendant (BUTA) + compaction par hash-consing.
// Version AUTONOME : aucune dépendance, C++17 pur.
//
// Réfs : Comon et al., TATA (2007) ; Daciuk et al., Comput. Linguistics (2000) ;
//        Filliâtre & Conchon, ML Workshop (2006).
//
//   Compilation :  g++ -std=c++17 -O2 -o tp tp_squelette.cpp
//   Exécution   :  ./tp
//
// Cherchez les blocs « TODO » : ce sont les seules zones à compléter.
// =============================================================================

#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

// -----------------------------------------------------------------------------
// 1. Alphabet classé (ranked alphabet) — symboles de l'arbre morphologique
// -----------------------------------------------------------------------------
enum class Node {
    PREFIX, ROOT, SUFFIX, NIL,        // arité 0 (feuilles, Σ₀)
    SUFFIXES, PREFIXES, REST, WORD    // arité 2 (nœuds binaires, Σ₂)
};

static const char* node_name(Node n) {
    switch (n) {
        case Node::PREFIX:   return "PREFIX";
        case Node::ROOT:     return "ROOT";
        case Node::SUFFIX:   return "SUFFIX";
        case Node::NIL:      return "NIL";
        case Node::SUFFIXES: return "SUFFIXES";
        case Node::PREFIXES: return "PREFIXES";
        case Node::REST:     return "REST";
        case Node::WORD:     return "WORD";
    }
    return "?";
}

// -----------------------------------------------------------------------------
// 2. Structure d'arbre  t ::= a  |  f(t1,...,tk)
// -----------------------------------------------------------------------------
struct Tree {
    Node type;
    std::string label;                       // morphème (feuilles) ou ""
    std::vector<std::shared_ptr<Tree>> kids; // fils (vide si feuille)
    Tree(Node t, std::string l = "") : type(t), label(std::move(l)) {}
};
using TreePtr = std::shared_ptr<Tree>;

static TreePtr mk(Node t, std::string l, std::vector<TreePtr> kids = {}) {
    auto n = std::make_shared<Tree>(t, std::move(l));
    n->kids = std::move(kids);
    return n;
}
// Fabriques pratiques
static TreePtr prefix(const std::string& s) { return mk(Node::PREFIX, s); }
static TreePtr root(const std::string& s)   { return mk(Node::ROOT, s); }
static TreePtr suffix(const std::string& s) { return mk(Node::SUFFIX, s); }
static TreePtr nil()                         { return mk(Node::NIL, ""); }

// notation lisible :  word(prefixes(...), rest(...))
static std::string to_str(const TreePtr& t) {
    if (!t) return "_";
    if (t->kids.empty())
        return std::string(node_name(t->type)) + "(\"" + t->label + "\")";
    std::string s = node_name(t->type);
    s += "(";
    for (size_t i = 0; i < t->kids.size(); ++i) {
        if (i) s += ", ";
        s += to_str(t->kids[i]);
    }
    return s + ")";
}

// Construit  word(prefixes-chain, rest(root, suffixes-chain))
// à partir de [prefix*], root, [suffix*].
static TreePtr build_word(const std::vector<std::string>& prefixes,
                          const std::string& root_str,
                          const std::vector<std::string>& suffixes) {
    TreePtr suf_chain = nil();
    for (auto it = suffixes.rbegin(); it != suffixes.rend(); ++it)
        suf_chain = mk(Node::SUFFIXES, "", {suffix(*it), suf_chain});
    TreePtr rest = mk(Node::REST, "", {root(root_str), suf_chain});
    TreePtr pre_chain = nil();
    for (auto it = prefixes.rbegin(); it != prefixes.rend(); ++it)
        pre_chain = mk(Node::PREFIXES, "", {prefix(*it), pre_chain});
    return mk(Node::WORD, "", {pre_chain, rest});
}

// -----------------------------------------------------------------------------
// 3. Automate d'arbre ascendant  A = (Q, Σ, F, Δ)
// -----------------------------------------------------------------------------
using State = int;
static const State REJECT = -1;

// États Q
enum : State {
    Q_PREFIX = 1, Q_ROOT, Q_SUFFIX, Q_NIL,
    Q_SUFFIXES, Q_PREFIXES, Q_REST, Q_WORD
};

struct Rule {
    Node f;                       // symbole
    std::vector<State> children;  // états des fils (vide pour une feuille)
    State result;                 // état produit
};

class BottomUpTA {
public:
    BottomUpTA() { build_rules(); }

    // run(t) : étiquette des feuilles vers la racine. Renvoie REJECT si aucune
    //          règle applicable quelque part dans l'arbre.
    State run(const TreePtr& t) const {
        if (!t) return REJECT;
        // -------------------------------------------------------------------
        // TODO (E1) : parcours POST-ORDRE.
        //   1. calculer récursivement l'état de CHAQUE fils ;
        //      si un fils renvoie REJECT, propager REJECT ;
        //   2. chercher une règle  f(q1,...,qk) -> q  qui matche
        //      (type == t->type ET états des fils identiques) ;
        //   3. renvoyer son 'result', ou REJECT si aucune ne matche.
        // -------------------------------------------------------------------
        (void)t;
        return REJECT;  // <-- à remplacer
    }

    // accepts(t) : vrai ssi run(t) ∈ F.
    bool accepts(const TreePtr& t) const {
        // TODO (E1) : renvoyer  run(t) ∈ final_states_
        (void)t;
        return false;   // <-- à remplacer
    }

    void add_rule(Node f, std::vector<State> kids, State res) {
        rules_.push_back({f, std::move(kids), res});
    }
    void add_final(State s) { final_.push_back(s); }

private:
    std::vector<Rule> rules_;
    std::vector<State> final_;

    bool is_final(State s) const {
        for (State f : final_) if (f == s) return true;
        return false;
    }

    void build_rules() {
        // Feuilles (Σ₀)
        add_rule(Node::PREFIX, {}, Q_PREFIX);
        add_rule(Node::ROOT,   {}, Q_ROOT);
        add_rule(Node::SUFFIX, {}, Q_SUFFIX);
        add_rule(Node::NIL,    {}, Q_NIL);
        // Chaînes de suffixes / préfixes (Σ₂)
        add_rule(Node::SUFFIXES, {Q_SUFFIX, Q_SUFFIXES}, Q_SUFFIXES);
        add_rule(Node::SUFFIXES, {Q_SUFFIX, Q_NIL},      Q_SUFFIXES);
        add_rule(Node::PREFIXES, {Q_PREFIX, Q_PREFIXES}, Q_PREFIXES);
        add_rule(Node::PREFIXES, {Q_PREFIX, Q_NIL},      Q_PREFIXES);
        // rest(root, suffixes)
        add_rule(Node::REST, {Q_ROOT, Q_SUFFIXES}, Q_REST);
        // TODO (E2) : ajouter la règle REST(Q_ROOT, Q_NIL) -> Q_REST
        //             (mot SANS suffixe, ex. "chien")
        // word(prefixes|nil, rest)
        add_rule(Node::WORD, {Q_PREFIXES, Q_REST}, Q_WORD);
        add_rule(Node::WORD, {Q_NIL,      Q_REST}, Q_WORD);
        // État final
        add_final(Q_WORD);
    }
public:
    // utilitaire de debug : nom lisible d'un état
    static const char* sname(State s) {
        switch (s) {
            case Q_PREFIX: return "Q_PREFIX"; case Q_ROOT: return "Q_ROOT";
            case Q_SUFFIX: return "Q_SUFFIX"; case Q_NIL: return "Q_NIL";
            case Q_SUFFIXES: return "Q_SUFFIXES"; case Q_PREFIXES: return "Q_PREFIXES";
            case Q_REST: return "Q_REST"; case Q_WORD: return "Q_WORD";
            default: return "REJECT";
        }
    }
};

// -----------------------------------------------------------------------------
// 4. Hash-consing  (compaction de la forêt en DAG)
// -----------------------------------------------------------------------------
using NodeId = std::int64_t;

class CompactStore {
public:
    // intern(t) : renvoie un NodeId UNIQUE par sous-arbre structurellement
    //             distinct. Deux sous-arbres ≡ partagent le même id.
    NodeId intern(const TreePtr& t) {
        if (!t) return -1;
        ++total_nodes_;
        // -------------------------------------------------------------------
        // TODO (E4) :
        //   1. interner récursivement chaque fils  -> vector<NodeId> kids_id ;
        //   2. clé canonique = (type, label, kids_id) ;
        //   3. si la clé est déjà dans la table -> renvoyer l'id existant
        //      SINON créer un nouvel id (= nodes_.size()), l'enregistrer,
        //      stocker (type,label,kids_id) pour pouvoir reconstruire (get).
        // -------------------------------------------------------------------
        (void)t;
        return -1;  // <-- à remplacer
    }

    // get(id) : reconstruit l'arbre interné (round-trip). À compléter en E5.
    TreePtr get(NodeId id) const {
        if (id < 0 || id >= (NodeId)nodes_.size()) return nullptr;
        const Entry& e = nodes_[id];
        std::vector<TreePtr> kids;
        for (NodeId c : e.kids) kids.push_back(get(c));
        return mk(e.type, e.label, kids);
    }

    size_t total_nodes()  const { return total_nodes_; }
    size_t unique_nodes() const { return nodes_.size(); }
    double compression()  const {
        return total_nodes_ ? 1.0 - double(nodes_.size()) / total_nodes_ : 0.0;
    }

private:
    struct Entry { Node type; std::string label; std::vector<NodeId> kids; };
    std::vector<Entry> nodes_;                 // id -> Entry  (pour get)
    std::map<std::string, NodeId> table_;      // clé canonique -> id
    size_t total_nodes_ = 0;

    // Vous pouvez utiliser ce helper pour fabriquer la clé canonique :
    static std::string key_of(Node t, const std::string& lbl,
                              const std::vector<NodeId>& kids) {
        std::string k = std::to_string((int)t) + ":" + lbl + ":";
        for (NodeId c : kids) { k += std::to_string(c); k += ","; }
        return k;
    }
    // (déclaré pour que le TODO puisse l'appeler ; libre à vous)
    friend int main();
};

// -----------------------------------------------------------------------------
// 5. Lot de test (petit vocabulaire anglais — redondance suffixale)
// -----------------------------------------------------------------------------
struct Word { std::vector<std::string> pre; std::string root; std::vector<std::string> suf; };

static std::vector<Word> sample_vocab() {
    return {
        {{"re"}, "structur", {"ation"}},   // re·structur·ation
        {{},     "happi",    {"ness"}},     // happi·ness
        {{"un"}, "happi",    {"ness"}},     // un·happi·ness
        {{},     "structur", {"ation"}},    // structur·ation
        {{},     "kind",     {"ness"}},     // kind·ness
        {{},     "play",     {"ing"}},      // play·ing
        {{},     "sing",     {"ing"}},      // sing·ing
        {{},     "chien",    {}},           // chien (sans suffixe)
        {{},     "cat",      {"s"}},        // cat·s
        {{},     "dog",      {"s"}},        // dog·s
    };
}

// -----------------------------------------------------------------------------
// 6. main : tests
// -----------------------------------------------------------------------------
int main() {
    BottomUpTA A;

    std::cout << "=== Partie A : reconnaissance (BottomUpTA) ===\n";
    auto w1 = build_word({"re"}, "structur", {"ation"});
    auto w2 = build_word({}, "chien", {});
    auto w3 = build_word({"un"}, "happi", {"ness"});
    std::cout << "  " << to_str(w1) << "\n";
    std::cout << "    accepts(re-structur-ation) = " << std::boolalpha
              << A.accepts(w1) << "   [attendu: true apres E1+E2]\n";
    std::cout << "    accepts(chien)             = " << A.accepts(w2)
              << "   [attendu: true apres E2]\n";
    std::cout << "    accepts(un-happi-ness)     = " << A.accepts(w3)
              << "   [attendu: true apres E1]\n";

    // E3 : arbre mal formé (SUFFIX la ou un ROOT est attendu)
    auto bad = mk(Node::WORD, "", {nil(),
                  mk(Node::REST, "", {suffix("oops"), nil()})});
    std::cout << "    accepts(arbre mal forme)   = " << A.accepts(bad)
              << "   [attendu: false]\n";

    std::cout << "\n=== Partie B : hash-consing (CompactStore) ===\n";
    CompactStore store;
    for (const auto& w : sample_vocab())
        store.intern(build_word(w.pre, w.root, w.suf));
    std::cout << "  total_nodes  = " << store.total_nodes()  << "\n";
    std::cout << "  unique_nodes = " << store.unique_nodes() << "\n";
    std::cout << "  compression  = " << store.compression()
              << "   [incoherent tant que E4 non fait ; vise ~0.45]\n";

    return 0;
}
