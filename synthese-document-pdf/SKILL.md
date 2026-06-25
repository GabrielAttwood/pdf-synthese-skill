---
name: synthese-document-pdf
description: >
  Transforme un document PDF (rapport, note d'analyse, article, étude) en une
  synthèse exécutive structurée, fidèle et sourcée. Produit toujours une synthèse
  Markdown ; si LaTeX est disponible sur la machine, produit en plus une version
  PDF mise en forme, prête à diffuser.
---

# Skill : Synthèse de document PDF

## Objectif

À partir d'un document PDF, produire une **synthèse exécutive claire, fidèle et
structurée**, exploitable directement (note de lecture, support de décision, base
de veille).

La synthèse doit permettre à un lecteur pressé de saisir l'essentiel sans lire le
document, tout en restant **traçable** : chaque affirmation renvoie à sa source.

> Tous les chemins ci-dessous sont relatifs au **dossier de travail courant**
> (là où l'utilisateur lance l'agent), et non au dossier d'installation du skill.

## Entrée

- Analyser le PDF indiqué par l'utilisateur (chemin fourni).
- À défaut de chemin, chercher un PDF dans le dossier de travail courant, ou dans
  un sous-dossier `pdf/` s'il existe.
- Si plusieurs PDF sont candidats, demander lequel analyser.
- Lire **l'intégralité** du document avant de rédiger. Ne pas se contenter du
  résumé ou de l'introduction.

### Préparation : ne pas se limiter au texte converti

Beaucoup de PDF ont une partie de leur contenu **uniquement dans des images** :
documents scannés, mises en page graphiques, **tableaux et figures intégrés en
image**. Lire le PDF seulement « en texte » fait alors rater des données
importantes (ou tout le document, s'il est scanné).

**Avant de rédiger**, extraire les images du PDF et les **regarder** :

```bash
python3 extract_images.py <document.pdf> images/
```

(Le script est fourni avec ce skill. Dépendances : `pip install pypdf pillow`.)

Il inspecte les objets image du PDF (`/XObject` de sous-type `/Image`), décode
leurs données et les écrit en PNG/JPG dans `images/`.

Ensuite :

- **Examiner visuellement** les images extraites (graphiques, tableaux, schémas),
  en plus du texte.
- Si le document est **principalement composé d'images** (texte converti vide ou
  incohérent), s'appuyer en priorité sur les images pour rédiger la synthèse.
- Reporter les **données chiffrées issues des tableaux/figures en image** dans la
  section « Données & faits marquants », en citant la page.

## Sortie

### 1. Rapport Markdown (toujours)

Créer un dossier `rapport/` dans le dossier de travail courant s'il n'existe pas,
puis y écrire le rapport dans `rapport/<nom-du-pdf>.md`, en suivant **exactement**
cette structure :

```
# <Titre du document> — <Auteur> (<année>)

## Résumé exécutif
<La thèse centrale et l'enjeu, en 5 lignes maximum.>

## Contexte & problématique
<Le problème posé, la question à laquelle le document répond.>

## Points clés
- <Argument ou conclusion 1> (p. X)
- <Argument ou conclusion 2> (p. X)
- ... (3 à 6 points, chacun avec la page ou la section d'origine)

## Données & faits marquants
- <Donnée chiffrée ou fait précis> (p. X)
- ...

## Termes & concepts clés
- **<Terme technique>** : <définition concise, en une phrase>
- ... (4 à 8 termes)

## À retenir
<Portée du document, implications, et limites éventuelles.>
```

### 2. Rapport PDF via LaTeX (si disponible)

Vérifier si LaTeX est installé sur la machine :

```bash
command -v pdflatex
```

- **Si `pdflatex` existe** : générer aussi `rapport/<nom-du-pdf>.tex` à partir du
  même contenu, puis le compiler en `rapport/<nom-du-pdf>.pdf`.
  - Utiliser une mise en page sobre (classe `article`, marges raisonnables).
  - Reprendre les mêmes sections que le rapport Markdown.
  - Compiler avec : `pdflatex -interaction=nonstopmode <fichier>.tex`
  - Nettoyer les fichiers auxiliaires (`.aux`, `.log`, `.out`) après compilation.
- **Si `pdflatex` n'existe pas** : ne pas générer de PDF, et indiquer à
  l'utilisateur que seul le Markdown a été produit (LaTeX non installé).

Gabarit LaTeX minimal à utiliser :

```latex
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage[margin=2.2cm]{geometry}
\usepackage[dvipsnames]{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\definecolor{accent}{rgb}{0.11,0.26,0.49}
\titleformat{\section}{\large\bfseries\color{accent}}{}{0em}{}
\setlist[itemize]{leftmargin=1.4em}
\begin{document}
% Titre + sections converties depuis le rapport Markdown
\end{document}
```

## Règles de fidélité (IMPORTANT)

Ces règles ne sont pas optionnelles. Elles garantissent un rapport fiable.

1. **Ne rien inventer.** Toute affirmation factuelle doit provenir du document.
2. **Citer la source** (page ou section) pour chaque argument et chaque chiffre.
3. **Signaler les manques.** Si une information est absente, ambiguë ou peu
   claire, l'écrire explicitement (ex. « non précisé dans le document »).
4. **Distinguer l'auteur de l'interprétation.** Ne pas présenter une déduction
   personnelle comme un propos de l'auteur.
5. **Ton neutre.** Pas de jugement personnel, pas d'opinion ajoutée.
6. **Langue** : rédiger le rapport dans la langue du document (français par
   défaut ici).

## Étapes d'exécution (résumé)

1. Identifier le PDF à analyser (chemin fourni, sinon dossier courant / `pdf/`).
2. Extraire les images (`extract_images.py`) et les **regarder**, en plus du texte.
3. Lire tout le document (texte + images).
4. Créer `rapport/` si besoin et y rédiger le rapport Markdown selon la structure imposée.
5. Tester `pdflatex` ; si présent, générer et compiler la version `.tex` → PDF.
6. Indiquer à l'utilisateur les fichiers produits.
