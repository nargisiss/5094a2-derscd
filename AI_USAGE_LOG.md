# Süni intellektdən istifadə jurnalı (nümunə)

Bu jurnalı real iş prosesinə uyğunlaşdırın; istifadə etmədiyiniz fəaliyyəti etmiş kimi göstərməyin.

| Sorğu/məqsəd | AI təklifi | Tələbənin yoxlaması və dəyişiklikləri | Öyrənilən anlayış |
|---|---|---|---|
| Layihə tələblərini modullara bölmək | Tədbir, istifadəçi, qeydiyyat və statistika modulları | Funksional tələblərlə tutuşduruldu | Modul bölgüsü |
| Verilənlər bazasını layihələndirmək | users, categories, events, registrations cədvəlləri | Xarici açarlar və UNIQUE(user_id, event_id) yoxlanıldı | Referensial bütövlük, unikal məhdudiyyət |
| Qeydiyyat qaydalarını qurmaq | Limit və təkrar qeydiyyat yoxlamaları | Normal və səhv hallar testlərlə yoxlanıldı | Backend validation |
| Testlər hazırlamaq | Əsas uğurlu və uğursuz ssenarilər | Testlər lokalda işə salınmalı, nəticələr buraya yazılmalıdır | Unit test, test client |

## Qeydlər
- AI-dən alınan kodu başa düşmədən təqdim etməyin.
- Testləri öz kompüterinizdə icra edin və faktiki nəticələri qeyd edin.
- Müdafiədə qəbul etdiyiniz texniki qərarları öz sözlərinizlə izah edin.
