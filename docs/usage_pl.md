# Uruchamianie APM-1

## Pliki i zależności

Rozpakuj całe repozytorium. Biblioteki pozostają w katalogu głównym,
a obwody w `examples`. Pobierając pojedynczy plik z GitHuba, użyj
jego surowej zawartości, nie strony HTML.

Plik w `examples` dołącza bibliotekę jako
`.include "../apm1_lib.txt"`. Wobulator wymaga dodatkowo
`.include "../apm1_wob_lib.txt"`. Dokumentacja, w tym dawne pliki RAG,
nie jest kodem do włączenia przez `.include`.
Ścieżki względne odnoszą się do pliku zawierającego dyrektywę; zachowaj
strukturę także przy kopiowaniu całego projektu.

## Uruchomienie i wyniki

W LTspice otwórz `examples/01_algebra.cir` poleceniem otwierania pliku,
a następnie wybierz Run. Netlista `.cir` jest samodzielnym wejściem
symulatora i nie wymaga schematu `.asc` ani symboli `.asy`.
W oknie przebiegów wybierz Add Trace i nazwy wskazane w
[indeksie przykładów](../examples/README.md).

W oknie SPICE Error Log odczytaj wyniki `.meas`. Przykłady z `.step`
tworzą wiele przebiegów i tabele wyników; wszystkie kroki muszą spełnić
odpowiednie kryteria. Znaczniki RESULTS są komentarzami porządkującymi kod,
nie poleceniem automatycznie rozstrzygającym poprawność.

Dla wykresu XY dodaj przebieg zależny, a następnie ustaw wyrażenie osi
poziomej na napięcie reprezentujące zmienną niezależną. W przykładzie
belki będą to np. `V(def_visual)` względem `V(x_pos)`; przeliczenie
osi pozycji na metry wynosi `L_real/VL`.

## Tworzenie własnego obwodu

Podaj mapowanie wielkości fizycznych na napięcie oraz czas symulacji.
Ostatni pin każdego bloku podłącz do `0`; nazwa `GDN` sama nie jest
automatycznie masą globalną. Piny i parametry odczytaj ze
[specyfikacji](reference_pl.md). Parametry są lokalne; wywołuj np.
`XM out a b 0 MUL VL={VL}`.

Dla integratorów jawnie wybierz znak i warunek początkowy.
Ustaw `leak=0`, jeżeli potrzebna jest dokładna całka bez zaniku.
Dla `INTV` podaj L, H oraz Taw; dla `RSTINT` dobierz Tr do długości
resetu. Nie ustawiaj wejścia resetu na 1 przez całą symulację, jeżeli
zamierzasz wykonywać swobodne całkowanie.

Przyjęte modele mają bufory idealne. `VL` nie jest napięciem zasilania;
wyjścia bloków algebraicznych nie są automatycznie ograniczane.
Logika sterująca używa zwykle poziomów 0/1 i progu 0.5.
`DAC8` również wymaga bitów 0/1. Przeskaluj sygnał 0/VL przed jego podaniem.

## Czas symulacji i dokładność

W postaci `.tran 0 Tstop 0 Maxstep` ostatnie pole ogranicza krok czasu.
Dla obwodów ciągłych rozpocznij od Maxstep nie większego niż 1/10 najmniejszej
istotnej stałej czasowej. Przy krótkich impulsach rozdzielczość musi
obejmować również ich szerokość. Dla potwierdzenia wyniku powtórz przebieg
z dwukrotnie mniejszym Maxstep i porównaj pomiary.

Gear może ograniczać artefakty numeryczne, ale nie dowodzi stabilności
matematycznej pętli. Okno uśredniania dobierz do wymaganej dokładności;
po 3 stałych czasowych pozostaje około 5% początkowego odchylenia,
po 7 około 0.09%. Dla rampy wynik końcowy odczytuj przez FIND/AT,
a średnią przez AVG/FROM/TO.

Biblioteka inicjalizuje swoje kondensatory stanu. `uic` pomija punkt
pracy i nie stanowi uniwersalnego rozwiązania problemów zbieżności.
W przykładzie D-12 użyto go świadomie dla jawnego kondensatora obwodu.
Kompresję danych wyłączono w przykładach kontrolnych przez plotwinsize=0.

## Wobulator

Otwórz [04_woblin.cir](../examples/04_woblin.cir), uruchom i porównaj
`V(w0)` oraz `V(w2)`. Przy VL=10, T=1 i leak=0 oba wyjścia mają
nachylenie 10 V/s; IC=2 przesuwa dojście do 10 V z 1 s na 0.8 s.
Nie jest to generator powtarzalny. Przy odwzorowaniu przedziału fizycznego
użyj X=Xmin+(Xmax-Xmin)*V(out)/VL.
Repozytorium nie zawiera kompletnego generatora profilu NACA; dawny
fragment instrukcji nie był takim programem.

## Wiersz poleceń i kontrola

Wymagany jest Python 3.10 lub nowszy. Z katalogu głównego:

```console
python tools/check_repository.py
python -m unittest discover -s tests -p "test_*.py" -v
python tools/run_ltspice.py --exe "C:\ścieżka\do\LTspice.exe"
```

Podaj rzeczywistą ścieżkę programu w swoim systemie.
Skrypt uruchamia `LTspice.exe -b` dla kopii obwodów w `build`,
odczytuje logi i porównuje wyniki z `tests/acceptance.json`.
Nie zmienia plików źródłowych. Kod wyjścia różny od zera oznacza brak
symulatora, błąd uruchomienia, brak pomiaru lub przekroczenie tolerancji.
Wyniki są zapisywane w `build/ltspice`; do zgłoszenia problemu dołącz
wersję LTspice, plik obwodu, log i raport JSON.

## Typowe problemy

Błąd znalezienia biblioteki wymaga sprawdzenia struktury i ścieżek,
a błąd liczby pinów — porównania wywołania z deklaracją `.subckt`.
Przy problemie zbieżności sprawdź znak sprzężenia, warunki początkowe,
nieciągłości i krok; dodawanie rzeczywistego upływu zmienia równanie zadania.

Dla dzielenia konieczny jest niezerowy mianownik i właściwy znak pętli.
Przykład 03 dostosowuje znak wzmocnienia do stałego mianownika
i sprawdza obydwa znaki. Zmienny mianownik przechodzący przez zero
wymaga osobno zaprojektowanej blokady i sposobu wznowienia obliczeń.

Eksport WAV ma pełną skalę ±1 V. Wyjścia audio przykładów zostały
znormalizowane. Memory.cir generuje krótki zapis diagnostyczny przy
10 MHz; nie jest to słyszalne odwzorowanie słowa bez rozciągnięcia czasu.

## Dokumentacja producenta

[Dyrektywy i pliki wynikowe](https://analogdevicesinc.github.io/ltspice-reference/ai_ref/SIMULATION-COMMANDS-REFERENCE.html)
oraz [uwagi producenta o całkowaniu behawioralnym](https://ez.analog.com/design-tools-and-calculators/ltspice/f/q-a/605623/idt-function-does-anymore-not-converge-in-tran-analysis/603992)
stanowiły dodatkowy kontekst wyboru jawnych stanów kondensatorowych.
