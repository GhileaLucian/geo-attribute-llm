# Rulare locala, fara credit OpenAI sau Claude

Ollama ruleaza modelul pe calculator. Nu este necesara o cheie API. Pagina
`Apps` din Ollama nu trebuie configurata pentru acest proiect; nu selecta
Claude Code sau Codex CLI pentru a porni benchmarkul.

Deschide PowerShell si intra in proiect:

```powershell
cd "C:\Users\Lucian Dan\Desktop\CV_Master_Hub_AI\02_CV_URI_PE_DOMENII\01_AI_si_Data_Science\geo-attribute-llm"
```

Deschide Ollama din meniul Start. Modelul se descarca o singura data:

```powershell
ollama pull qwen2.5:3b
```

Daca terminalul deschis inainte de instalare nu recunoaste `ollama`, deschide
un terminal nou sau foloseste executabilul instalat:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
```

## Interfata aplicatiei

```powershell
python -m streamlit run app.py
```

Deschide http://localhost:8501, selecteaza `local` din lista extractorului,
alege un segment si apasa `Extract`. Nu selecta `openai` sau `claude` daca
nu vrei sa folosesti acele API-uri. Oprirea interfetei: Ctrl+C in terminal.

## Benchmark si rapoarte

```powershell
python run_pipeline.py --mode local --split dev --prompt-version v1
python run_pipeline.py --mode local --split hard --prompt-version v1
```

`dev` are 40 de inregistrari OSM cu atribute ascunse. `hard` are 15 scenarii
fictive, inclusiv descrieri in romana. Scorurile sunt raportate separat.
Nu folosi `--split test` pentru ajustarea prompturilor: este setul hold-out.

Terminalul afiseaza progresul pentru fiecare inregistrare. Prima extragere
poate dura mai mult pentru incarcarea modelului. Rapoartele si predictiile
apar in subfolderele `reports/local__...`; `reports/comparison.md` compara
rularile salvate. `results/raw/local/` pastreaza raspunsurile si tokenii.

Repetarea unei comenzi identice refoloseste raspunsurile salvate. Pentru
recalcularea raportului fara model pornit:

```powershell
python run_pipeline.py --mode local --split dev --prompt-version v1 --cached-only
```

Dupa rezolvarea unei erori, repeta doar extragerile esuate cu `--retry-failed`.
Nu exista inlocuire automata cu baseline-ul: erorile raman vizibile.

Costul de API este zero pentru modul local; calculatorul consuma resurse
si energie. Validarea JSON nu garanteaza corectitudinea atributelor.
Nu publica `.env`, chei API sau fisierele modelului pe GitHub.
