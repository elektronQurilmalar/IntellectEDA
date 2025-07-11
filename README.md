# IntellectEDA
Dastruriy ta'minot internetdan elektron komponent yoki muayyan interfeysga oid hujjatlarni topadi. Bu dastur elektroniklar uchun juda foydali.
Программа для поиска application note для компонента или интерфейса. Больше подходит для инженера-схемотехника.
The programm finds datasheetsб refer to components or interfaces. More suitable for a electronics engineers. 
<img width="997" height="672" alt="image" src="https://github.com/user-attachments/assets/3be28522-bacb-40da-9fad-9f9d6e7918b7" />
<img width="992" height="676" alt="image" src="https://github.com/user-attachments/assets/c991b4d4-23ac-48af-87d6-dcb1f2c305e3" />
<img width="995" height="672" alt="image" src="https://github.com/user-attachments/assets/0163992d-7cd3-4850-aa09-3b9133040a89" />

DIQQAT!!!!!

Veb-qidiruv funksiyasini ishga tushirish uchun Google API’ni sozlash talab etiladi. Bu bepul va taxminan 5 daqiqa vaqt oladi.
1-qadam: API kalitini (API Key) olish
Google Cloud Console sahifasiga o'ting.
Agar loyihangiz bo'lmasa, yangi loyiha yarating (masalan, uni AN-Finder deb nomlang).
+ CREATE CREDENTIALS tugmasini bosing va API key (API kaliti) bandini tanlang.
Yaratilgan kalitdan nusxa oling. U sizga keyinroq kerak bo'ladi.
(Tavsiya etiladi) Xavfsizlik uchun kalitdan foydalanishni cheklang: ro'yxatdagi kalitni bosing, "API restrictions" bo'limida "Restrict key" ni tanlang va ochilgan ro'yxatda faqat "Custom Search API" ga ruxsat bering.
2-qadam: Qidiruv tizimini (Custom Search Engine) yaratish
Programmable Search Engine boshqaruv paneliga o'ting.
Add (Qo'shish) tugmasini bosing.
"What to search?" (Nima qidirilsin?) bo'limida Search the entire web (Butun Internet bo'ylab qidirish) opsiyasini tanlang. Bu juda muhim!
Qidiruv tizimingiz uchun ixtiyoriy nom kiriting (masalan, AN-Finder Search).
Create (Yaratish) tugmasini bosing.
Keyingi sahifada Search engine ID (Qidiruv tizimi identifikatori) dan nusxa oling.
3-qadam: Loyihada API'ni yoqish
Google Cloud API kutubxonasiga o'ting.
To'g'ri loyiha tanlanganiga ishonch hosil qiling (1-qadamdagi loyiha).
Qidiruv maydoniga Custom Search API deb yozing.
Natijalardan "Custom Search API" ni tanlang.
Moviy rangdagi ENABLE (Yoqish) tugmasini bosing.
4-qadam: Loyihani sozlash
Loyiha papkasida config.py faylini toping.
Uni oching va nusxa olingan qiymatlaringizni joylashtiring:
Generated python
# config.py
API_KEY = "API_KALITINGIZNI_SHU_YERGA_JOYLASHTIRING"
CSE_ID = "QIDIRUV_TIZIMI_IDENTIFIKATORINI_SHU_YERGA_JOYLASHTIRING"
Use code with caution.
Python
Muhim: Maxfiy kalitlaringizni tasodifan GitHub'da e'lon qilmaslik uchun config.py faylini .gitignore faylingizga qo'shing.
Endi dastur ishlashga tayyor
