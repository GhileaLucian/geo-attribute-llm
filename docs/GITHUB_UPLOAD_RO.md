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
git commit -m "Add local Ollama inference and measured prompt comparisons"
git push origin main
```

.env este ignorat. Se publica numai .env.example, cu valori goale pentru chei.
Publica aplicatia, testele, documentatia, datele OSM si rezultatele salvate.
Aceasta actualizare include modul local Ollama / Qwen2.5 3B, cele 165 de
raspunsuri pentru v1/v2/v3, rapoartele separate OSM / cazuri fictive si analiza
castigurilor si regresiilor din reports/prompt_iterations.md.

Incercarile OpenAI esuate sunt pastrate ca dovezi de erori de infrastructura
(credit API insuficient), nu ca masuratori ale preciziei modelului. Claude nu
a fost benchmarkat. Testele automate nu necesita chei API sau Ollama instalat.

Nu publica .env, chei, greutatile modelului, mediul Python local sau CV-ul cu
date personale. Fisierele .gguf si .ollama/ sunt ignorate; modelul se descarca
separat pe calculator. Verifica fisierele pregatite inainte de fiecare commit.

push_to_github.bat foloseste folderul in care se afla scriptul si publica
ramura curenta. Daca exista fisiere necomise, se opreste si afiseaza starea.
Nu creeaza automat un commit si nu foloseste force push.

Acest ghid descrie pasii pentru publicarea modificarilor locale si a
rezultatelor viitoare. Verifica istoricul repository-ului pentru commiturile publicate.
