# Przykłady LTspice

Pliki `.cir` są samodzielnymi netlistami. Otwórz wybrany plik w LTspice
i wybierz Run; następnie dodaj wskazane przebiegi oraz otwórz SPICE Error Log.
[Instrukcja](../docs/usage_pl.md) opisuje wszystkie kroki.
Wartości poniżej są wynikami oczekiwanymi z równań, nie zapisem wykonanej symulacji.

## Minimalny zestaw

| Plik | Co pokazuje | Przebiegi i wartości kontrolne |
|---|---|---|
| [01_algebra.cir](01_algebra.cir) | Wzmocnienie, suma, mnożenie i jawne VL | `V(sum)=5`, `V(product)=6`, `V(normalized)=6/VL`; trzy kroki VL=5,10,20. |
| [02_integrator.cir](02_integrator.cir) | Znak, IC, współczynnik K i podtrzymanie | Przy t=1: positive=3, negative=1, scaled=4, noninverting=3, constant=3. |
| [03_division.cir](03_division.cir) | Dzielenie przez stały mianownik dodatni i ujemny | `V(nom_c)` dąży do ±2; `V(nom_e)` zanika ze stałą 2.222222 ms; sześć kombinacji VL i znaku B. |
| [04_woblin.cir](04_woblin.cir) | Rozszerzenie WOBLIN, IC i ograniczenie | `V(w0)` osiąga 10 V po 1 s, `V(w2)` po 0.8 s; po 0.5 s odpowiednio 5 V i 7 V. |
| [05_sampling.cir](05_sampling.cir) | Poziomy logiczne, zegar, detektor zbocza i pamięć | `V(held)` około 0.5 V podczas pierwszej przerwy śledzenia, impuls `V(edge)` około 20 µs. |

Pełne zakresy akceptacji są zapisane w [acceptance.json](../tests/acceptance.json).
Przykłady nie wymagają symboli ani dodatkowych modeli producentów.
`04_woblin.cir` dołącza obie biblioteki; pozostałe tylko główną.

## Pozostałe przykłady i zgodność

[Opis przykładów zaawansowanych](../docs/advanced_examples_pl.md) obejmuje
trójkąt, belkę, helisę, równanie D-12, pamięć i modele historycznych systemów.
Długie dawne komentarze przeniesiono do [archiwum](../docs/examples/README.md);
aktualne instrukcje pozostają w dokumentacji, a netlisty zawierają kod.

Główny plik `division.cir` dołącza przykład 03.
Dawne pliki `Integral equation (D-12 brochure)en.cir` i
`Integral equation (D-12 brochure)pl.cir` dołączają
[integral_equation_d12.cir](integral_equation_d12.cir).
Są to trzy wejścia zgodności, nie trzy dodatkowe testy.
Plik `APM1_GEE_DEMO.cir` nie ma już spacji na początku nazwy.

Testy regresji stanu, filtrów i logiki znajdują się w `tests/*.cir`.
Uruchomienie całego zestawu:
`python tools/run_ltspice.py --suite all --exe "C:\\ścieżka\\LTspice.exe"`.

