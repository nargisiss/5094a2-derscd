# Universitet Tədbirlərinin İdarə Edilməsi və Qeydiyyat Sistemi

Flask, SQLite, HTML, CSS və JavaScript istifadə edən tədris layihəsi.

## Tələblər
- Python 3.10 və ya daha yeni
- İnternet yalnız Flask paketini ilk dəfə quraşdırmaq üçün lazımdır

## İşə salınma (Windows)
1. ZIP faylını çıxarın və layihə qovluğunu açın.
2. Terminalda həmin qovluğa keçin.
3. Virtual mühit yaradın:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Asılılıqları quraşdırın:
   ```bash
   pip install -r requirements.txt
   ```
5. Tətbiqi başladın:
   ```bash
   python app.py
   ```
6. Brauzerdə `http://127.0.0.1:5000` ünvanını açın.

İlk başladıqda `events.db` bazası və nümunə tədbirlər avtomatik yaradılır.

## Demo administrator
- E-poçt: `admin@university.az`
- Şifrə: `Admin123!`

Bu giriş məlumatları yalnız lokal nümayiş üçündür. Real yerləşdirmədən əvvəl şifrəni dəyişin və `SECRET_KEY` mühit dəyişənini təyin edin.

## Funksiyalar
- Tədbirlərə baxış, ad üzrə axtarış, kateqoriya, tarix aralığı və yer üzrə filtr
- Hesab yaratmaq, daxil olmaq və çıxış
- Tədbirə qeydiyyat və qeydiyyatı ləğv etmək
- Təkrar qeydiyyatın qarşısının alınması və tutum limitinin yoxlanılması
- Admin paneli, tədbir yaratmaq/redaktə etmək/silmək
- Ümumi statistika, kateqoriyalar üzrə statistika və ən populyar tədbirlər
- İştirakçı siyahısı və CSV ixracı
- Parolların hash formasında saxlanması və parametrli SQL sorğuları

## Verilənlər bazası
- `users`: istifadəçilər və rol
- `categories`: tədbir kateqoriyaları
- `events`: tədbir məlumatları
- `registrations`: istifadəçi-tədbir əlaqəsi; `UNIQUE(user_id, event_id)` təkrar qeydiyyatı bloklayır

## Testlər
`python -m unittest discover -s tests -v`

## Git
```bash
git init
git add .
git commit -m "Initial university event management system"
```
Dəyişiklikləri etdikcə ayrıca, mənalı commit-lər yaradın.

## Qeyd
Bu layihə dərs məqsədlidir. İctimai serverdə istifadə etməzdən əvvəl CSRF qoruması, rate limiting, daha güclü sessiya konfiqurasiyası, təhlükəsiz deployment və ayrıca admin parolunun idarə edilməsi əlavə olunmalıdır.
