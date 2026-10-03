# Zasady generowania obwodów APM-1

Najpierw odczytaj [specyfikację](reference_pl.md), deklaracje `.subckt`
i najbliższy działający przykład. Stwierdzoną sprzeczność opisu z kodem
należy zgłosić, a nie ukrywać przez wybór wygodniejszej wersji.

Używaj wyłącznie rzeczywistych nazw bloków i pełnej listy pinów.
Ostatni pin instancji głównego obwodu łącz z 0. Jawnie przekazuj VL
do bloków z tym parametrem. Nie dodawaj nieistniejącego bloku MUX.
Nie kopiuj instrukcji Markdown ani dokumentacji do pliku biblioteki.

Nazwij sposób reprezentacji sygnałów i czasu. Rozróżnij iloczyn
znormalizowany od liczbowego, stan od wyjścia ograniczonego oraz
reset o skończonym czasie od natychmiastowego nadpisania wartości.
Nie utożsamiaj rezystora przy idealnym źródle z upływem całki.
Parametr leak integratorów zmienia równanie; w DIF służy jedynie
zgodności starych wywołań i musi być równy 0.

Dopuszczalne są zarówno obwody oparte na blokach APM-1, jak i jawnie
oznaczone obwody hybrydowe z natywnymi źródłami, rezystorami i kondensatorami.
Źródła testowe nie muszą być konstruowane z integratorów.

Każdy samodzielny przykład ma nagłówek, zależności, parametry, opcje,
jedną analizę przejściową, pomiary w bloku RESULTS i końcowe .end.
Wyjątkiem są opisane pliki zgodności dołączające kompletny przykład.
Kod wykonywalny utrzymuj w jednym pliku; tłumaczenia opisu mogą być osobne.

Wartości oczekiwane oblicz z równania niezależnie od symulatora.
Określ tolerancję i wszystkie kroki .step. Odróżniaj kontrolę struktury,
test równania i rzeczywistą symulację LTspice. Nie deklaruj wykonania
testu, jeżeli istnieje jedynie jego opis lub netlista.
Archiwalne komentarze w docs/examples nie stanowią aktualnej specyfikacji.
