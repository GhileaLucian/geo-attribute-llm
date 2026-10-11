# Configurarea Claude API

Cheia este a contului tau. Nu este furnizata de acest proiect sau de asistent.

1. Intra in [Claude Console](https://platform.claude.com/).
2. Deschide Settings -> API keys si creeaza o cheie personala pentru proiect.
3. Verifica Settings -> Billing pentru creditele API disponibile.
4. In folderul proiectului, copiaza .env.example in .env.
5. Completeaza ANTHROPIC_API_KEY in .env, local. Nu o publica pe GitHub.

Documentatie: [crearea cheii](https://platform.claude.com/docs/en/get-api-key),
[facturare](https://support.claude.com/en/articles/8977456-how-do-i-pay-for-my-claude-api-usage).

Conform documentatiei consultate la 11 octombrie 2026, planurile Max si Team
eligibile pot include credite API lunare, care trebuie revendicate prin
conectarea organizatiei Console. Free si Pro nu sunt eligibile pentru aceste
credite. Verifica planul si soldul propriului cont:
[credite API pentru abonati](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers).

PowerShell:

```powershell
Copy-Item .env.example .env
notepad .env
python run_pipeline.py --mode claude --split dev --prompt-version v1
```

In .env:

```dotenv
ANTHROPIC_API_KEY=completeaza_local
ANTHROPIC_MODEL=claude-sonnet-5-5
```

ID-ul implicit este cel din documentatia Claude consultata:
[modele API](https://platform.claude.com/docs/en/models/overview).
Il poti schimba cu ANTHROPIC_MODEL sau --model. Disponibilitatea pentru contul
tau trebuie verificata printr-un apel real.

Pentru o singura cerere, deschide dashboard-ul:

```powershell
python -m streamlit run app.py
```

Alege Claude si apasa Extract. Schimbarea selectiei nu face apeluri API.
Rezultatul este salvat si poate fi refolosit daca modelul, promptul si intrarea
sunt identice. Erorile nu sunt inlocuite cu raspunsuri baseline.

Testeaza mai intai pe dev. Compara versiunile v1, v2, v3 pe acelasi set.
Alege versiunea inainte sa folosesti --split test. Iteratiile si testul final
nu au fost executate in repo-ul pregatit fara cheia ta.

Preturile nu sunt fixate in cod. Daca vrei o estimare, completeaza
INPUT_USD_PER_MILLION si OUTPUT_USD_PER_MILLION dupa pretul modelului ales.
Fara preturi si utilizare raportata, costul apare null, nu zero.
Estimarea nu este factura si nu trateaza separat cache-ul promptului furnizorului.
