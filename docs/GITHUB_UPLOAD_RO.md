# Incarcarea proiectului pe GitHub

Copia actualizata este in folderul geo-attribute-llm din CV_Master_Hub_AI.
Exista si o alta copie pe Desktop; aceasta runda a modificat numai copia din hub.

Repository remote: https://github.com/GhileaLucian/geo-attribute-llm

In PowerShell, din acest folder:

```powershell
git status --short
git diff --stat
python -m pytest -q
git check-ignore .env
git add .gitignore .gitattributes .env.example .github README.md requirements.txt run_pipeline.py app.py create_notebook.py push_to_github.bat src tests docs data notebooks reports results assets
git diff --cached --stat
git commit -m "Add masked OSM benchmark, recorded extraction and offline checks"
git push origin main
```

.env este ignorat. Se publica numai .env.example, cu valori goale pentru chei.
Rezultatele baseline, datele OSM si rapoartele pot fi incluse in commit.
Dupa o rulare reala Claude, verifica si adauga si noile rezultate/rapoarte.

push_to_github.bat foloseste folderul in care se afla scriptul si publica
ramura curenta. Daca exista fisiere necomise, se opreste si afiseaza starea.
Nu creeaza automat un commit si nu foloseste force push.

Acest ghid descrie pasii pentru publicarea modificarilor locale si a
rezultatelor viitoare. Verifica istoricul repository-ului pentru commiturile publicate.
