# EasyFALC

## Le but

EasyFALC est une application web multiplateforme d’aide à la création de texte « facile à lire et à comprendre » (FALC).

Il suffit de saisir votre texte dans la zone prévue à cet effet, puis de presser sur « évaluer ».

Tous les éléments non conformes seront mis en évidence. Un clic sur un de ces éléments fera apparaitre une suggestion de correction sur la droite.

## Technologies et utilisations

* Flask & venv
  * [Installation](http://flask.pocoo.org/docs/0.12/installation/#installation)
  * [Quickstart](http://flask.pocoo.org/docs/0.12/quickstart/#)
* TinyMCE (Editeur WYSIWYG)

### Installation
```
C:\> venv\Scripts\activate.bat
C:\> pip install flask # si nécessaire
C:\> set FLASK_RUN=hello.py
C:\> flask run
```

## Processus de fonctionnement

1. Entrée du text par l'utilisateur;
2. Envoi du formulaire;
3. Suppression des balises HTML;
4. Traîtement du texte, recherche d'erreurs;
5. Rafraîchissement de la page;
6. Affichage du nouveau text à l'aide de balise HTML afin de mettre en surbrillance les erreurs et déclencher des événements pour afficher les messages d'erreurs sur le côté.

## Architecture du projet

### Fichiers

**hello.py**
Lancé en tant que main par flask, décrit les routes des urls.

**util.py**
Méthodes utiles, appelées par le main (`hello.py`)

**dictionaries.db**
Le dictionnaire principal qui pourrait être utilisé pour la fréquence des mots.

### Dossiers

**venv/**
Propre à venv

**dict/**
Des dictionnaires (lexique, thesaurus, fréquences) qui ont été trouvés. Ces derniers ont été pensé utiles pour la suite du projet.

Contient aussi `particles.txt` fichier qui est utiliser pour stocker des types de particules à éviter ainsi qu'un message d'avertissement pour l'utilisateur. Le format du document doit suivre cette structure:

- Trois lignes par particle
- Ligne 1: Expression régulière
- Ligne 2: Message d'information concernant la mitigation à effectuer
- Ligne 3: Type de particule (word, punc, endi)

Les types de particule sont décrites comme suit pour l'instant:
 - word: Un type de mot à éviter (ne, n', un mot d'un certain nombre de caractère)
 - punc: Une ponctuation à éviter (:();: etc.)
 - endi: Temps de verbe à éviter (pas encore implémenté)

**static/**
Fichiers statiques pour l'interface web flask. (css, javascript, images, polices d'écriture)

**templates/**

Template `jinja2` utilisés par flask.
