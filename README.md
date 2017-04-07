# EasyFALC

## Le but

EasyFALC est une application web multiplateforme d’aide à la création de texte « facile à lire et à comprendre » (FALC).

Il suffit de saisir votre texte dans la zone prévue à cet effet, puis de presser sur « évaluer ».

Tous les éléments non conformes seront mis en évidence. Un clic sur un de ces éléments fera apparaitre une suggestion de correction sur la droite.

## Utilisation

Flask + venv, à utiliser comme suit:

```
C:\> venv\Scripts\activate.bat
C:\> pip install flask # si nécessaire
C:\> set FLASK_RUN=hello.py
C:\> flask run
```

## Architecture du projet

### hello.py

Lancé en tant que main par flask, décrit les routes des urls.

### util.py

Méthodes utiles, appelées par le main (`hello.py`)

### dictionaries.db

Le dictionnaire principal qui pourrait être utilisé pour la fréquence des mots.

### Dossier: venv

Propre à venv

### Dossier: dict

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

### Dossier: static

Fichiers statiques pour l'interface web flask. (css, javascript, images, polices d'écriture)

### Dossier: templates

Template `jinja2` utilisés par flask.
