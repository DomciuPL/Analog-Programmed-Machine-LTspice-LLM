# Migracja z b7a5d54 do 2.0.0-rc.1

## Zmiany wpływające na wyniki

W integratorach leak oznacza teraz rzeczywisty zanik stanu, w 1/s.
Dawna gałąź równoległa do idealnego źródła napięcia jedynie je obciążała.
Jeżeli wcześniejszy obwód używał niezerowego leak jako rzekomego środka
poprawy zbieżności, należy świadomie wybrać fizyczny upływ albo leak=0.

INTV ogranicza wyjście oraz koryguje stan przez sprzężenie z czasem Taw.
Stan nie jest idealnie zaciskany; opisuje go pełne równanie w specyfikacji.
Nie należy oczekiwać dawnego nieograniczonego narastania ukrytej całki.

RSTINT resetuje rzeczywisty kondensator stanu z czasem Tr.
Wyjście nie jest przełączane na fikcyjną wartość podczas swobodnego
całkowania wewnętrznego. Impuls resetu powinien trwać co najmniej 20*Tr.

LP1/HP1 oraz integratory mają jawne kondensatory; lokalne .ic wymagają
podłączenia GDN do 0. SCHMITT i MONO otrzymały jawny stan początkowy,
zamiast algebraicznego odwołania wyjścia do samego siebie.
Ograniczenia czasowania MONO zapisano w specyfikacji.

DIF zachowuje idealny tryb dla tau=0 i dodaje ograniczenie pasma dla tau>0.
Jego dawny leak nie jest filtrem i pozostaje tylko parametrem zgodności.
EDGE_R/F wykrywają teraz przejście przez próg, nie dowolne narastanie
lub opadanie sygnału analogowego. CLK uwzględnia czasy zboczy przy
ustalaniu wypełnienia; duty=0 i duty=1 tworzą stałe.

## Pliki i zgodność ścieżek

Główne nazwy bibliotek i kolejność dotychczasowych pinów zostały zachowane.
Dodane parametry mają wartości domyślne. W przykładach jawnie przekazano
VL do bloków, zachowując uzasadnione lokalne ustawienia VL=1.

division.cir jest wejściem zgodności do examples/03_division.cir.
Dwie wersje językowe przykładu D-12 dołączają jedną netlistę kanoniczną.
Usunięto początkową spację z nazwy APM1_GEE_DEMO.cir.
Dawne ścieżki plików instrukcji i RAG odsyłają do aktualnej dokumentacji.

W przykładzie helisy leak=0 zachowuje dokładną interpretację geometryczną.
Przykład trójkąta ma IC=-A i prawidłowo opisany znak różniczkowania.
Wyniki GEE opisane jako końcowe odczytują punkt końcowy.
Wektor kierunku (0.7,0.3) został znormalizowany, aby moduł prędkości
wynosił zadane 400 km/h. Dawniej wynosił około 304.63 km/h.
Jednostkę czasową modelu GEE wyprowadzono z jednostki drogi i prędkości światła.
Wyjścia audio są normalizowane, a Memory używa zapisu diagnostycznego
dostosowanego do mikrosekundowych bitów.

Dla równania faktycznie zapisanego w D-12 i y(0)=0.25 warunek y(1)=1
odpowiada A≈0.446965927, a nie A=0.2563 z dawnego komentarza.
Nie potwierdzono wierności przepisania równania z broszury.
Zachowano równanie i cztery dawne wartości A; przebiegi wydłużono
do analitycznie wyznaczonego x_stop, odpowiadającego Y_STOP=0.99.
Pomiar y_at_1 pozwala odczytać wartość w dawnym punkcie końcowym.
Nie jest to sztuczne ograniczanie mianownika ani deklaracja, że dawne
przebiegi przekraczały osobliwość przed x=1.

## Status

Wersja rc wymaga wykonania zestawu akceptacyjnego w docelowym LTspice.
Kontrole Python nie stanowią certyfikacji symulatora ani modeli fizycznych.
Zakres i sposób powtórzenia testów opisuje [raport](validation_pl.md).
