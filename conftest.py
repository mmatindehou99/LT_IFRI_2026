# Permet à pytest d'importer formlang/ et apps/ depuis la racine.
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
