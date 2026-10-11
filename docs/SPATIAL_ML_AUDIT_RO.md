# Audit ML: zonă geografică separată și ablația coordonatelor

Audit de clasificare offline, fără LLM/API. Nu înlocuiește rapoartele vechi și
nu modifică modelul ori hiperparametrii după scor. Predicția este familia
drumului derivată din tag-ul OSM `highway`, nu adevăr verificat în teren.

## Rezultatul măsurat

F1 ponderat, pe același test pentru toate cele trei modele din fiecare rând:

| Split | Train / test | Majoritar | Forest cu coordonate | Forest fără coordonate |
| --- | ---: | ---: | ---: | ---: |
| Grupuri după nume/ID | 11.042 / 3.549 | 0,290 | 0,703 | 0,660 |
| Zonă estică + buffer | 10.432 / 3.601 | 0,178 | 0,629 | 0,632 |

Pe split-ul geografic, eliminarea coordonatelor nu reduce F1: diferența este
aproximativ +0,003. Pe split-ul pe grupuri, reducerea este aproximativ 0,043.
Acest audit **nu susține** concluzia că scorul vechi era „în mare parte geografie”.
Nu dovedește nici absența oricărei scurgeri de informație. Scorurile dintre cele
două rânduri nu sunt o comparație pe aceleași înregistrări: zona estică are alt
amestec de clase, vizibil inclusiv în scorul baseline-ului majoritar.

## Regula de split, stabilită înainte de fit

- EPSG:32634, metri. Pragul x este percentila 75 a centroizilor tuturor drumurilor.
- Test: geometria completă este la est de prag, nu doar centroidul.
- Train: geometria completă este la vest de prag minus 200 m.
- Drumurile care traversează limita și grupurile de train care apar în test sunt
  excluse. În această rulare: 558 excluse; suprapunere de grupuri zero;
  separare minimă pe axa x a geometriilor: 201,26 m.
- Random Forest: 100 arbori, adâncime maximă 10, seed 42; fără căutare de parametri.
  Imputarea mediană este ajustată numai pe train. `highway` nu este feature.
  Ablația elimină doar centroid_x_m și centroid_y_m; păstrează aceleași înregistrări.

O singură regiune și un buffer reduc contaminarea imediată între vecini, nu
toate corelațiile spațiale. Nu este cross-validation spațială. Lungimea,
numărul nodurilor și benzile pot reflecta practica de cartografiere. Regresia
veche rămâne exploratorie; nu i-am atribuit aici un rezultat spațial nou.

## Reproducere și artefacte

```powershell
python run_spatial_ml_audit.py --output reports/spatial_ml_audit_reproduction
```

Un folder existent este refuzat, ca să nu suprascriem rezultate. Compară
[raportul complet](../reports/spatial_ml_audit/summary.json) și
[ID-urile split-urilor](../reports/spatial_ml_audit/splits.json).
Cod: `src/spatial_ml_audit.py`; testele verifică separarea geometriilor,
grupurilor și aceleași înregistrări pentru ablație. Nu modifica parametrii
pentru a îmbunătăți rezultatul pe această zonă de test.
