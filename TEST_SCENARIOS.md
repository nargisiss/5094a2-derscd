# Test ssenariləri

| № | Ssenari | Gözlənilən nəticə |
|---|---|---|
| 1 | Ana səhifəni açmaq | HTTP 200 və tədbirlər görünür |
| 2 | Ad üzrə uyğun tədbir axtarmaq | Uyğun tədbir göstərilir |
| 3 | Nəticə verməyən axtarış | “Uyğun tədbir tapılmadı” mesajı görünür |
| 4 | Daxil olmadan qeydiyyat düyməsi | İstifadəçi giriş səhifəsinə yönləndirilir |
| 5 | İstifadəçinin tədbirə qeydiyyatı | Qeydiyyat bazaya yazılır |
| 6 | Eyni tədbirə təkrar qeydiyyat | İkinci qeydiyyat yaradılmır |
| 7 | Tutumu dolmuş tədbirə yeni qeydiyyat | Qeydiyyat rədd edilir |
| 8 | Adi istifadəçinin admin panelini açması | Admin icazəsi rədd edilir |

Testləri icra etmək üçün: `python -m unittest discover -s tests -v`. Nəticə sütununu testləri öz mühitinizdə icra etdikdən sonra doldurun.
