// ta_check.cpp — reconnaissance d'arbres morphologiques (Exercices 3.1 & 3.3).
//
// Construit quelques arbres, les soumet à l'automate, affiche accept/reject, la
// frontière (yield) et la classe morphologique. À ÉTENDRE (zone TODO) avec vos cas.
//
// Compilation : make ta_check     (ou : g++ -std=c++17 -O2 ta_check.cpp -o ta_check)

#include "tree_automaton.hpp"
#include <iostream>

using namespace ta;

static void show(const std::string& nom, const TreePtr& t) {
    TreeAutomaton A;
    std::cout << (A.accepts(t) ? "ACCEPT  " : "REJECT  ")
              << class_name(classify(A, t)) << "\t" << nom
              << "   [yield=\"" << yield(t) << "\"]\n";
}

int main() {
    // --- doivent ÊTRE ACCEPTÉS (les 4 classes, Ex. 3.3) ---------------------
    // BARE : racine seule
    show("BARE livre",
        word(nil(), rest(root("livre"), nil())));
    // SUFFIXED : racine + suffixe  (jou+er)
    show("SUFFIXED jou-er",
        word(nil(), rest(root("jou"), suffixes(suffix("er"), nil()))));
    // PREFIXED : préfixe + racine  (na+penda)
    show("PREFIXED na-penda",
        word(prefixes(prefix("na"), nil()), rest(root("penda"), nil())));
    // CIRCUMFIXED : préfixes + racine + suffixe  (a-na-pend-a)
    show("CIRCUMFIXED a-na-pend-a",
        word(prefixes(prefix("a"), prefixes(prefix("na"), nil())),
             rest(root("pend"), suffixes(suffix("a"), nil()))));

    // --- doivent ÊTRE REJETÉS (Ex. 2.3) -------------------------------------
    // (a) un suffixe à la place de la racine
    show("MALFORMÉ rest(suffix,nil)",
        word(nil(), rest(suffix("er"), nil())));
    // (b) une racine dans la chaîne de suffixes (root au lieu de suffix)
    {   TreeAutomaton A;
        auto bad = std::make_shared<Tree>();
        bad->kind = Kind::Word;
        bad->kids = { nil(),
                      rest(root("a"), inner(Kind::Suffixes, root("b"), nil())) };
        std::cout << (A.accepts(bad) ? "ACCEPT  " : "REJECT  ")
                  << "—\tMALFORMÉ suffixes(root,nil)\n";
    }

    // === TODO (étudiant) ====================================================
    // 1. Ajoutez d'autres mots de votre langue et vérifiez leur classe.
    // 2. Construisez un 3e arbre mal formé et vérifiez qu'il est REJETÉ.
    // 3. (Ex. 3.4) Étendez l'automate pour l'infixation : dérivez une sous-classe,
    //    appelez add_rule()/add_final(), reconnaissez s<um>ulat.
    return 0;
}
