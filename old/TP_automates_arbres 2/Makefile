# Makefile — TP « Automates d'arbres » (autonome ; aucune dépendance hors g++/python3).

CXX      := g++
CXXFLAGS := -std=c++17 -O2 -Wall

.PHONY: all run corpora clean

all: ta_check morph_demo

ta_check: ta_check.cpp tree_automaton.hpp
	$(CXX) $(CXXFLAGS) ta_check.cpp -o ta_check

morph_demo: morph_demo.cpp tree_automaton.hpp
	$(CXX) $(CXXFLAGS) morph_demo.cpp -o morph_demo

corpora:
	python3 gen_corpora.py

run: all corpora
	@echo "=== (1) Reconnaissance d'arbres (Ex. 3.1 / 3.3) ==="
	./ta_check
	@echo
	@echo "=== (2) Surface -> arbre -> automate, sur deux corpus (Ex. 4) ==="
	./morph_demo corpus_A_prefixing.txt corpus_B_suffixing.txt

clean:
	rm -f ta_check morph_demo
