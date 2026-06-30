# Permet à pytest d'importer formlang/ et apps/ depuis la racine.
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
