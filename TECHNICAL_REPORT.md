# Texniki sənəd

## Məqsəd
Universitet tədbirlərinin yaradılması, axtarışı, qeydiyyatı və statistik idarə edilməsi üçün web tətbiqi.

## Texnologiyalar
- **Frontend:** HTML, CSS, Jinja şablonları və kiçik interaktivlik üçün brauzer imkanları.
- **Backend:** Python və Flask marşrutları.
- **Database:** SQLite; xarici açarlar və unikal qeydiyyat məhdudiyyəti aktivdir.
- **Versiya nəzarəti:** Git.
- **AI:** tələblərin təhlili, ilkin kod izahı və test ssenariləri üçün köməkçi vasitə; faktiki istifadəni AI_USAGE_LOG.md-də qeyd edin.

## Arxitektura
Brauzer HTTP sorğusunu Flask backend-ə göndərir. Backend daxil olan məlumatları yoxlayır, parametrli SQL sorğuları ilə SQLite bazasına müraciət edir və nəticəni Jinja şablonu ilə HTML kimi qaytarır.

## Məlumat bazası
- `users(id, full_name, email, password_hash, role, created_at)`
- `categories(id, name)`
- `events(id, title, description, category_id, event_date, event_time, location, capacity, created_at)`
- `registrations(id, user_id, event_id, registered_at)`

`events.category_id` `categories.id`-yə; `registrations.user_id` `users.id`-yə; `registrations.event_id` `events.id`-yə istinad edir. `UNIQUE(user_id,event_id)` təkrar qeydiyyatın qarşısını alır. `capacity > 0` CHECK məhdudiyyəti tutumu yoxlayır. Qeydiyyat limiti backend-də də yoxlanılır.

## OOP, Clean Code və SOLID
Flask tətbiqi kiçik tədris layihəsi kimi funksiyalar və marşrutlar üzrə bölünüb. Təkrar edilən DB bağlantısı `get_db()` funksiyasında, giriş və admin yoxlamaları dekoratorlarda mərkəzləşdirilib. Daha böyük istehsal layihəsində route, service və repository qatlarını ayrıca modullara ayırmaq məqsədəuyğundur.

## Təhlükəsizlik
SQL sorğuları parametrli yazılıb, şifrələr Werkzeug hash funksiyası ilə saxlanılır, admin marşrutları rol yoxlamasından keçir. Bu dərs nümunəsi istehsal üçün hazır deyil: CSRF qoruması, giriş cəhdlərinin məhdudlaşdırılması, təhlükəsiz SECRET_KEY və deployment konfiqurasiyası əlavə edilməlidir.

## İşə salınma və test
README.md təlimatlarına baxın. Testlər `python -m unittest discover -s tests -v` ilə işə salınır. Test nəticələrini yalnız real icradan sonra hesabatda qeyd edin.
