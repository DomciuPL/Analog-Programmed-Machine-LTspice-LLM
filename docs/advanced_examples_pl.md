# Przykłady zaawansowane

Wartości kontrolne wyprowadzono z równań obwodów. Nie są wynikami
uzyskanymi w LTspice podczas przygotowania tej wersji.
Formalne tolerancje podano w [acceptance.json](../tests/acceptance.json),
a stan weryfikacji w [raporcie](validation_pl.md).
Kod znajduje się wyłącznie w plikach `.cir`; archiwalne komentarze
mogą zawierać dawne błędy.

## Sygnały, geometria i pamięć

| Netlista | Interpretacja i sposób oglądania | Wynik oczekiwany |
|---|---|---|
| [Trójkąt i prostokąt](../examples/APM1_TRI2SQ_A1_F200_v1.cir) | Dodaj V(tri), V(y), V(y01). INT startuje z IC=-A; DIF ma ujemne K. | Trójkąt około ±1 V przy 200 Hz; Y_neg=-1, Y_pos=+1, Y01_dut≈0.5. Skończone zbocza powodują małe odchylenie amplitudy. |
| [Belka wspornikowa](../examples/CANTILEVER%20BEAM.cir) | Czas 0..1 s reprezentuje x=0..10 m. V(x_pos)=VL*x/L; deflect reprezentuje metry, shear niutony, moment niutonometry. Wykres XY: V(def_visual) względem V(x_pos), skala pozioma L/VL. | Dla q(x)=Q*(1-(x/L)^2): siła i moment na końcu ≈0; ugięcie końca = -19*Q*L^4/(360*EI) = -1.055555556 m. V(def_visual) ma znak przeciwny. |
| [Helisa](../examples/Helisa_apm_1_.cir) | Dodaj V(x1), V(y1), V(z); rzuty perspektywiczne to x1p/y1p/zp. Współczynnik nm2VL mapuje nanometry na wolty. | Przy t=1: th=10π, z=17.85, pitch_est=3.57 nm/obrót. leak=0 jest konieczne dla tych zależności. To idealizacja geometryczna, nie model mechaniki cząsteczki. |
| [Pamięć opóźniająca](../examples/Memory.cir) | V(write), V(nIN_LOOP), V(nDELAY_RAW), V(BIT_SHAPED); słowo 997 = 1111100101, bit 2 µs. | Tloop≈20 µs. Próg VL/2 wytwarza logikę 0/1, następnie GAIN odtwarza 0/VL. Zapis WAV 10 MHz daje 20 próbek na bit i trwa tylko 200 µs; służy diagnostyce. |

Belka używa jawnych jednostek liczbowych; napięcia nie są ograniczone do ±VL.
Jej zakres obciążenia i ugięcia nie stanowi obliczenia wytrzymałościowego
konkretnej konstrukcji. Obwody łączą bloki APM-1 z natywnymi źródłami SPICE,
co jest dopuszczonym trybem użycia biblioteki.

## Równanie D-12

[Netlista kanoniczna](../examples/integral_equation_d12.cir) zachowuje
równanie poprzedniego kodu:

\[
\frac{dy}{dx} =
\frac{A y(1+0.14y)(1+0.02752y)}{(1-y)(1-Ax)},\qquad y(0)=0.25.
\]

Przyjęto x równy czasowi symulacji, a stan y reprezentuje napięcie
kondensatora 1 F ładowanego prądem odpowiadającym prawej stronie.
Ponieważ równanie jest osobliwe przy y=1, nie należy symulować
przejścia przez ten punkt przez arbitralne obcięcie mianownika.

Dla a=0.14 i b=0.02752 rozdzielenie zmiennych daje
Φ(y)-Φ(0.25)=-ln(1-Ax), gdzie

\[
\Phi(y)=\ln y-\frac{1+a}{a-b}\ln(1+ay)
                  +\frac{1+b}{a-b}\ln(1+by).
\]

Stąd warunek graniczny y(1)=1 odpowiada
A=1-exp(-(Φ(1)-Φ(0.25)))≈0.44696592685.
W tym punkcie pochodna jest nieograniczona; jest to wartość graniczna
rozwiązania, nie regularny punkt równania różniczkowego.
Dawna deklaracja A=0.2563 nie wynikała z zapisanego równania.
Nie zweryfikowano zgodności jego transkrypcji z oryginalną broszurą D-12,
więc ta korekta nie rozstrzyga treści źródła historycznego.

Zachowano kroki A=0.3, 0.2927, 0.2571, 0.2563.
Każdy przebieg kończy się przy analitycznie wyznaczonym x_stop dla
Y_STOP=0.99: odpowiednio około 1.4898071, 1.5269632, 1.7383980, 1.7438242.
Oczekuje się y_stop≈0.99; y_at_1 zachowuje odczyt w dawnym końcu analizy.
Zmieniaj Y_STOP tylko w przedziale (0.25,1), przy A>0.
Powyższa postać Φ zakłada różne, dodatnie a i b.
Po zmianie parametrów trzeba ponownie dobrać krok czasu i kryteria pomiarów.

## Modele historycznych systemów

Są to demonstracje matematyczne sygnałów, ruchu i porównywania czasów.
Nie obejmują pełnego toru radiowego, balistyki ani rekonstrukcji urządzeń.
Nazwy historyczne nie oznaczają potwierdzenia zgodności wszystkich założeń
z dokumentacją techniczną epoki.

| Netlista | Sygnały i założenia modelu | Wartości kontrolne przy parametrach domyślnych |
|---|---|---|
| [GEE](../examples/APM1_GEE_DEMO.cir) | V(y) względem V(x); V(dMB), V(dMC) to różnice odległości, V(tMB), V(tMC) to odpowiadające różnice czasu. Skale: 20 km/V i 100 s czasu fizycznego na 1 s symulacji. | Po 2 s: x≈-2.978727744, y≈-2.562311890. Kierunek (0.7,0.3) jest normalizowany, więc prędkość wynosi 400 km/h. |
| [Oboe](../examples/APM1_OBOE_DEMO.cir) | V(phi), V(x), V(y), V(r_cat), V(r_mouse), V(pulse_M); ruch po okręgu, r_jam=0. | t_drop≈30.5683562 s, rcat_drop≈rmouse_drop≈4; dT_err≈0. |
| [Y-Gerät](../examples/APM1_Y_GERAET_DEMO.cir) | V(x), V(x_meas), V(pulse_ideal), V(pulse_Y); stały ruch i x_jam=0. | Czas obu zdarzeń ≈40 s; dT_err≈0, dX_err≈0. |
| [X-Gerät](../examples/X_GERAET_DEMO.cir) | V(r), V(tO), V(tE), V(dT), V(tauE), V(pulse_rel). S_H śledzi czas przez całe okno 20 ms. | t_Rhine≈10 s, t_Oder≈30 s, t_Elbe≈35 s, t_rel≈40.0199 s. dT_OE≈5 s; dT_ER jest większe o około 19.9 ms. |
| [Knickebein](../examples/KNICKEBEIN_APM1.cir) | V(audio_a), V(audio_b) oraz przebiegi bramkowania i wag sa/sb. | Oba maksima modułu audio mieszczą się w (0,1]; WAV stereo ma zapas amplitudy dzięki mnożnikowi 0.8/VL. |
| [Lorenz](../examples/RAF_LORENZ_SCENARIO_APM1.cir) | V(audio), V(ctrl_dot), V(ctrl_dash) i waga V(s). | Szczyt modułu i RMS audio są dodatnie oraz nie przekraczają pełnej skali WAV. |
| [Model Dopplera V2](../examples/V2.cir) | V(vM), V(fDM), V(fHz), V(dop). Przyjęto vFS=2000 m/s, VL=10, fTB=30 MHz i modelowy współczynnik 4 w zależności Dopplera. | Po 10 s: vM=10, prędkość fizyczna 2000 m/s, fD_final=800 Hz. |

W GEE parametr D_MC_km zachował dawną nazwę, ale wyznacza współrzędną Y
stacji C, a nie długość A–C. Jednostkę 20 km i jej odpowiednik czasowy
zdefiniowano na potrzeby modelu; oba przeliczenia są obecnie zgodne.
W X-Gerät opóźnienie pamięci analogowej wynika z okna śledzenia oraz
Ron*Ch=100 µs. Oczekiwanie idealnie równych interwałów byłoby błędne.

Obwody audio bywają kosztowniejsze obliczeniowo. Zestaw `--suite all`
obejmuje je, ale domyślny zestaw `core` ogranicza się do podstaw i
testów stanu, filtrów oraz logiki.

