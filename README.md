# designs
Correr los siguientes comandos:
- pip install virtualenv
- virtualenv venv
- venv\Scripts\activate
- pip install -r requirements.txt

## Organizacion del proyecto:
 - Modulo por cada area de funcionalidad (i.e. "pdfs" module handles all PDF opperations, "container" module handles container opperations, etc)
 - Tests folder has a subfolder per module and a test file per file in that module that requires testing

## How to test
 - run `pytest` to execute all the tests in the project