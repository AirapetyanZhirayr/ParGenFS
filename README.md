Parsimonious Generalization of Fuzzy Sets

This project is about generalizing fuzzy sets, built on Data Science publications in Journal of Classification.

run.ipynb -  script to run the whole project. This script will guide you through the whole project and will make you understand which file in which order to open.

Description of other files:

  loading_Abstracts.ipynb - scrapping publications and their abstracts.

  papers.csv - the dataset of scraped abstracts

  JoC_publications_1984_2019.docx - full list of publications

  СС_Taxonomy.csv, СС_Taxonomy.xlsx - The taxonomy tree in DS domain given by [Boris Mirkin](https://www.hse.ru/staff/bmirkin), Professor of the Faculty of Computer
  Science at HSE.

  R.txt - paper_text to taxonomy_topic relevance matrix build on AST.

  ete3_functions.py и visualize.py -utils for visualization 

  lapin.py - laplace inverse transformation

  U_matrix.txt' - topic to topic relevance matrice with laplace inverse transformation applied
  
  ParGen.py - the algorithm of the parsimonious generalization of given fuzzy set
  
  table.csv - the results

