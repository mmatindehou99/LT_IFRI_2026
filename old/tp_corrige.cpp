// =============================================================================
// TP — Automates d'arbres : CORRIGÉ ENSEIGNANT (réservé)
// Théorie des langages — Master GL, IFRI
//
//   g++ -std=c++17 -O2 -o tp_corrige tp_corrige.cpp && ./tp_corrige
//
// Version autonome. Les zones « TODO » du squelette sont ici résolues
// et commentées (BUTA + hash-consing).
// =============================================================================

#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <vector>

// ---- 1. Alphabet classé ----------------------------------------------------
enum class Node {
    PREFIX, ROOT, SUFFIX, NIL,        // Σ₀ (arité 0)
    SUFFIXES, PREFIXES, REST, WORD    // Σ₂ (arité 2)
};
static const char* node_name(Node n) {
    switch (n) {
        case Node::PREFIX:   return "PREFIX";   case Node::ROOT:     return "ROOT";
        case Node::SUFFIX:   return "SUFFIX";   case Node::NIL:      return "NIL";
        case Node::SUFFIXES: return "SUFFIXES"; case Node::PREFIXES: return "PREFIXES";
        case Node::REST:     return "REST";     case Node::WORD:     return "WORD";
    }
    return "?";
}

// ---- 2. Arbre --------------------------------------------------------------
struct Tree {
    Node type; std::string label;
    std::vector<std::shared_ptr<Tree>> kids;
    Tree(Node t, std::string l = "") : type(t), label(std::move(l)) {}
};
using TreePtr = std::shared_ptr<Tree>;
static TreePtr mk(Node t, std::string l, std::vector<TreePtr> kids = {}) {
    auto n = std::make_shared<Tree>(t, std::move(l));
    n->kids = std::move(kids); return n;
}
static TreePtr prefix(const std::string& s) { return mk(Node::PREFIX, s); }
static TreePtr root(const std::string& s)   { return mk(Node::ROOT, s); }
static TreePtr suffix(const std::string& s) { return mk(Node::SUFFIX, s); }
static TreePtr nil()                         { return mk(Node::NIL, ""); }

static std::string to_str(const TreePtr& t) {
    if (!t) return "_";
    if (t->kids.empty())
        return std::string(node_name(t->type)) + "(\"" + t->label + "\")";
    std::string s = node_name(t->type); s += "(";
    for (size_t i = 0; i < t->kids.size(); ++i) { if (i) s += ", "; s += to_str(t->kids[i]); }
    return s + ")";
}
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

// ---- 3. BottomUpTA ---------------------------------------------------------
using State = int;
static const State REJECT = -1;
enum : State { Q_PREFIX = 1, Q_ROOT, Q_SUFFIX, Q_NIL,
               Q_SUFFIXES, Q_PREFIXES, Q_REST, Q_WORD };
struct Rule { Node f; std::vector<State> children; State result; };

class BottomUpTA {
public:
    BottomUpTA() { build_rules(); }

    // === CORRIGÉ E1 : run en post-ordre ===
    State run(const TreePtr& t) const {
        if (!t) return REJECT;
        std::vector<State> cs;
        for (const auto& k : t->kids) {        // 1. fils d'abord (bottom-up)
            State s = run(k);
            if (s == REJECT) return REJECT;     //    propagation du rejet
            cs.push_back(s);
        }
        for (const auto& r : rules_) {          // 2. règle f(q1..qk) -> q
            if (r.f != t->type) continue;
            if (r.children.size() != cs.size()) continue;
            bool ok = true;
            for (size_t i = 0; i < cs.size(); ++i)
                if (r.children[i] != cs[i]) { ok = false; break; }
            if (ok) return r.result;            // 3. état produit
        }
        return REJECT;                          //    aucune règle -> rejet
    }
    // === CORRIGÉ E1 : accepts ===
    bool accepts(const TreePtr& t) const {
        State s = run(t);
        return is_final(s);
    }
    void add_rule(Node f, std::vector<State> kids, State res) {
        rules_.push_back({f, std::move(kids), res});
    }
    void add_final(State s) { final_.push_back(s); }

    // version instrumentée pour Q2 (affiche l'état à chaque nœud)
    State run_trace(const TreePtr& t, int depth = 0) const {
        if (!t) return REJECT;
        std::vector<State> cs;
        for (const auto& k : t->kids) {
            State s = run_trace(k, depth + 1);
            if (s == REJECT) return REJECT;
            cs.push_back(s);
        }
        State out = REJECT;
        for (const auto& r : rules_) {
            if (r.f != t->type || r.children.size() != cs.size()) continue;
            bool ok = true;
            for (size_t i = 0; i < cs.size(); ++i)
                if (r.children[i] != cs[i]) { ok = false; break; }
            if (ok) { out = r.result; break; }
        }
        std::cout << "    " << std::string(depth * 2, ' ')
                  << node_name(t->type)
                  << (t->label.empty() ? "" : ("(\"" + t->label + "\")"))
                  << " -> " << sname(out) << "\n";
        return out;
    }

    static const char* sname(State s) {
        switch (s) {
            case Q_PREFIX: return "Q_PREFIX"; case Q_ROOT: return "Q_ROOT";
            case Q_SUFFIX: return "Q_SUFFIX"; case Q_NIL: return "Q_NIL";
            case Q_SUFFIXES: return "Q_SUFFIXES"; case Q_PREFIXES: return "Q_PREFIXES";
            case Q_REST: return "Q_REST"; case Q_WORD: return "Q_WORD";
            default: return "REJECT";
        }
    }
private:
    std::vector<Rule> rules_; std::vector<State> final_;
    bool is_final(State s) const {
        for (State f : final_) if (f == s) return true;
        return false;
    }
    void build_rules() {
        add_rule(Node::PREFIX, {}, Q_PREFIX);
        add_rule(Node::ROOT,   {}, Q_ROOT);
        add_rule(Node::SUFFIX, {}, Q_SUFFIX);
        add_rule(Node::NIL,    {}, Q_NIL);
        add_rule(Node::SUFFIXES, {Q_SUFFIX, Q_SUFFIXES}, Q_SUFFIXES);
        add_rule(Node::SUFFIXES, {Q_SUFFIX, Q_NIL},      Q_SUFFIXES);
        add_rule(Node::PREFIXES, {Q_PREFIX, Q_PREFIXES}, Q_PREFIXES);
        add_rule(Node::PREFIXES, {Q_PREFIX, Q_NIL},      Q_PREFIXES);
        add_rule(Node::REST, {Q_ROOT, Q_SUFFIXES}, Q_REST);
        add_rule(Node::REST, {Q_ROOT, Q_NIL},      Q_REST);   // === CORRIGÉ E2 ===
        add_rule(Node::WORD, {Q_PREFIXES, Q_REST}, Q_WORD);
        add_rule(Node::WORD, {Q_NIL,      Q_REST}, Q_WORD);
        add_final(Q_WORD);
    }
};

// ---- 4. Hash-consing -------------------------------------------------------
using NodeId = std::int64_t;
class CompactStore {
public:
    // === CORRIGÉ E4 : intern (congruence structurelle) ===
    NodeId intern(const TreePtr& t) {
        if (!t) return -1;
        ++total_nodes_;
        std::vector<NodeId> kids_id;
        for (const auto& k : t->kids) kids_id.push_back(intern(k)); // 1. récursif
        std::string key = key_of(t->type, t->label, kids_id);       // 2. clé
        auto it = table_.find(key);
        if (it != table_.end()) return it->second;                  // 3a. partage
        NodeId id = (NodeId)nodes_.size();                          // 3b. nouveau
        nodes_.push_back({t->type, t->label, kids_id});
        table_.emplace(key, id);
        return id;
    }
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
    std::vector<Entry> nodes_;
    std::map<std::string, NodeId> table_;
    size_t total_nodes_ = 0;
    static std::string key_of(Node t, const std::string& lbl,
                              const std::vector<NodeId>& kids) {
        std::string k = std::to_string((int)t) + ":" + lbl + ":";
        for (NodeId c : kids) { k += std::to_string(c); k += ","; }
        return k;
    }
};

// ---- 5. Lot de test --------------------------------------------------------
struct Word { std::vector<std::string> pre; std::string root; std::vector<std::string> suf; };
static std::vector<Word> sample_vocab() {
    return {
        {{"re"}, "structur", {"ation"}}, {{}, "happi", {"ness"}},
        {{"un"}, "happi", {"ness"}},     {{}, "structur", {"ation"}},
        {{}, "kind", {"ness"}},          {{}, "play", {"ing"}},
        {{}, "sing", {"ing"}},           {{}, "chien", {}},
        {{}, "cat", {"s"}},              {{}, "dog", {"s"}},
    };
}

// ---- 6. main ---------------------------------------------------------------
int main() {
    BottomUpTA A;

    std::cout << "=== Q2 : deroule de run sur re-structur-ation ===\n";
    auto w1 = build_word({"re"}, "structur", {"ation"});
    State top = A.run_trace(w1);
    std::cout << "  => racine = " << BottomUpTA::sname(top)
              << " ; accepte = " << std::boolalpha << A.accepts(w1) << "\n\n";

    std::cout << "=== Partie A : reconnaissance ===\n";
    auto w2 = build_word({}, "chien", {});
    auto w3 = build_word({"un"}, "happi", {"ness"});
    std::cout << "  accepts(re-structur-ation) = " << A.accepts(w1) << "\n";
    std::cout << "  accepts(chien)             = " << A.accepts(w2) << "\n";
    std::cout << "  accepts(un-happi-ness)     = " << A.accepts(w3) << "\n";
    auto bad = mk(Node::WORD, "", {nil(),
                  mk(Node::REST, "", {suffix("oops"), nil()})});
    std::cout << "  accepts(arbre mal forme)   = " << A.accepts(bad)
              << "  (run casse au REST : SUFFIX la ou Q_ROOT est requis)\n\n";

    std::cout << "=== Partie B : hash-consing ===\n";
    CompactStore store;
    NodeId id_struct = -1, id_struct2 = -1;
    int idx = 0;
    for (const auto& w : sample_vocab()) {
        NodeId id = store.intern(build_word(w.pre, w.root, w.suf));
        if (idx == 0) id_struct  = id;   // re·structur·ation
        if (idx == 3) id_struct2 = id;   // structur·ation
        ++idx;
    }
    std::cout << "  total_nodes  = " << store.total_nodes()  << "\n";
    std::cout << "  unique_nodes = " << store.unique_nodes() << "\n";
    std::cout << "  compression  = " << store.compression() << "\n";

    std::cout << "\n=== E5 : partage de sous-arbres ===\n";
    // Les chaines suffixes 'ation', 'ness', 'ing', 's' sont partagees.
    // Round-trip exact :
    auto rebuilt = store.get(id_struct);
    std::cout << "  round-trip(re-structur-ation) == original ? "
              << (to_str(rebuilt) == to_str(build_word({"re"},"structur",{"ation"})))
              << "\n";
    std::cout << "  (les sous-arbres suffixes communs sont fusionnes :\n"
                 "   p.ex. rest(ROOT 'structur', suffixes('ation')) reapparait\n"
                 "   dans re-structur-ation ET structur-ation)\n";

    return 0;
}
