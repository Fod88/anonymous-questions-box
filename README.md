# Anonymous Questions Box

مشروع **Web Application** بسيط يسمح لأي زائر بإرسال سؤال أو رسالة (باسمه أو بشكل Anonymous) إلى الـ Admin، بدون الحاجة إلى إنشاء حساب. الـ Admin يملك لوحة تحكم محمية لعرض الرسائل، تحديدها كمقروءة، وحذفها.

## 🧱 Tech Stack

- **Backend:** Python + Flask
- **Database:** SQLite
- **Frontend:** HTML + CSS + JavaScript (Jinja2 Templates)
- **Auth:** Flask Sessions + Werkzeug Password Hashing

## 📁 Project Structure

```text
project/
│
├── app.py                     # Main Flask app (routes + API)
├── config.py                  # App configuration (reads from .env)
├── database.py                # DB connection + init + schema
├── requirements.txt
├── .env.example
├── .gitignore
├── database.db                 # Created automatically on first run
│
├── templates/
│   ├── base.html
│   ├── index.html              # Welcome page (choose name / anonymous)
│   ├── messages.html           # Page to write & send a message
│   │
│   └── admin/
│       ├── login.html
│       └── dashboard.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── main.js             # Welcome page + send message logic
│       └── dashboard.js        # Admin dashboard logic
│
├── translations/
│   ├── en.json                 # English strings (for future i18n)
│   └── ar.json                 # Arabic strings (for future i18n)
│
└── README.md
```

> **ملاحظة عن الترجمة:** الواجهة الحالية بالإنجليزية (Default) بشكل مباشر داخل الـ HTML. ملفات `translations/en.json` و `translations/ar.json` موجودة كأساس لإضافة Language Switcher لاحقًا بسهولة دون الحاجة لإعادة هيكلة المشروع.

## ⚙️ المتطلبات

- Python 3.10 أو أحدث
- pip

## 🚀 خطوات التشغيل على Windows

1. **فك ضغط المشروع** ثم افتح **Command Prompt** أو **PowerShell** داخل مجلد المشروع.

2. **إنشاء Virtual Environment (اختياري لكن يُفضّل):**

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. **تثبيت المكتبات المطلوبة:**

   ```powershell
   pip install -r requirements.txt
   ```

4. **إنشاء ملف `.env`:**

   انسخ الملف `.env.example` وأعد تسميته إلى `.env`، ثم عدّل القيم:

   ```powershell
   copy .env.example .env
   ```

   محتوى `.env` (مثال):

   ```env
   SECRET_KEY=your-random-secret-key-here
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=YourStrongPassword123
   ```

5. **تشغيل المشروع:**

   ```powershell
   python app.py
   ```

   عند أول تشغيل، سيقوم الكود تلقائيًا بـ:
   - إنشاء ملف قاعدة البيانات `database.db`.
   - إنشاء جدولي `messages` و `admins`.
   - إنشاء حساب Admin افتراضي (إن لم يكن موجودًا) بالبيانات الموجودة في `.env`.

6. **افتح المتصفح على:**

   ```text
   http://127.0.0.1:5000
   ```

   - صفحة المستخدم العادي: `http://127.0.0.1:5000/`
   - صفحة دخول الـ Admin: `http://127.0.0.1:5000/admin/login`

## 🗄️ إنشاء قاعدة البيانات يدويًا (اختياري)

قاعدة البيانات تُنشأ تلقائيًا عند تشغيل `python app.py`. لكن إذا أردت إنشاءها يدويًا دون تشغيل السيرفر:

```powershell
python -c "from app import app; from database import init_db; init_db(app)"
```

لإعادة إنشاء قاعدة بيانات جديدة تمامًا، احذف ملف `database.db` ثم شغّل الأمر السابق (أو شغّل `python app.py`) من جديد.

## 🔑 Admin Credentials (تجريبية فقط)

القيم الافتراضية إذا لم تُغيّر `.env`:

```text
Username: admin
Password: admin123
```

> ⚠️ **مهم جدًا:** هذه البيانات للتجربة والتطوير المحلي فقط. **يجب تغييرها** قبل رفع المشروع لأي بيئة حقيقية (Production)، وذلك عبر تعديل `ADMIN_USERNAME` و `ADMIN_PASSWORD` في ملف `.env` **قبل أول تشغيل** (لأن الحساب يُنشأ مرة واحدة فقط إذا لم يكن موجودًا).
>
> إذا أردت تغيير كلمة المرور بعد إنشاء الحساب، احذف السطر الخاص به من جدول `admins` في `database.db` ثم أعد تشغيل المشروع بقيم `.env` الجديدة، أو حدّث القيمة مباشرة عبر كود بسيط باستخدام `generate_password_hash`.

## 🔌 API Endpoints

### Public (لا يحتاج تسجيل دخول)

| Method | Endpoint          | الوصف                              |
|--------|-------------------|-------------------------------------|
| POST   | `/api/messages`   | إرسال رسالة جديدة                  |

**Body (JSON):**
```json
{
  "message": "نص الرسالة",
  "username": "Ali"   // اختياري، افتراضيًا Anonymous
}
```

**Responses:**
- `201` — تم الإرسال بنجاح.
- `400` — الرسالة فارغة أو طويلة جدًا / الـ username طويل جدًا.

### Admin Only (يتطلب تسجيل دخول Admin)

| Method | Endpoint                        | الوصف                          |
|--------|----------------------------------|---------------------------------|
| GET    | `/api/messages`                 | جلب جميع الرسائل (الأحدث أولاً) |
| PATCH  | `/api/messages/<id>/read`       | تحديد رسالة كمقروءة             |
| DELETE | `/api/messages/<id>`            | حذف رسالة                       |

**Responses الشائعة:** `200`, `401` (غير مسجل دخول), `404` (الرسالة غير موجودة).

## 🔒 الأمان (Security)

- كلمات مرور الـ Admin مخزنة بصيغة Hash فقط باستخدام `werkzeug.security.generate_password_hash`.
- التحقق من الدخول عبر `check_password_hash`.
- جلسات Flask (`Session`) لحفظ حالة تسجيل الدخول، مع `HttpOnly` و `SameSite=Lax`.
- كل الـ Admin Routes و الـ Admin API محمية بـ `login_required` decorator.
- الـ `SECRET_KEY` وبيانات الـ Admin توضع في `.env` وليس داخل الكود مباشرة.
- Input Validation على الرسائل (فارغة / طويلة جدًا) وعلى الـ username.

## ☁️ رفع المشروع على GitHub

1. تأكد من وجود `.gitignore` (موجود بالفعل) لتجنب رفع `database.db` و `.env` والملفات المؤقتة.

2. من داخل مجلد المشروع:

   ```bash
   git init
   git add .
   git commit -m "Initial commit: Anonymous Questions Box"
   ```

3. أنشئ Repository جديد فارغ على GitHub (بدون README أو .gitignore من GitHub نفسه لتفادي التعارض).

4. اربط الـ Remote وارفع المشروع:

   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

5. **لا تنسَ:** لا يتم رفع `.env` أبدًا (موجود في `.gitignore`). أي شخص يستنسخ المشروع يجب أن ينشئ `.env` خاص به من `.env.example`.

## ✅ الميزات المطبقة

- إرسال رسائل Anonymous أو باسم مختار، بدون حساب أو Password.
- عدد غير محدود من الرسائل لكل مستخدم.
- Admin Login محمي بـ Session + Password Hashing.
- Admin Dashboard: عرض الرسائل (الأحدث أولًا)، عدد الرسائل، عدد غير المقروءة.
- Mark as Read و Delete لكل رسالة.
- REST API منظم بأكواد HTTP صحيحة (200, 201, 400, 401, 404).
- تصميم Responsive بألوان فاتحة ومريحة، يعمل على Desktop / Tablet / Mobile.
- بنية جاهزة لإضافة الترجمة العربية لاحقًا دون تعقيد إضافي.

## 🚫 خارج نطاق المشروع (بالتصميم)

لا يحتوي المشروع على: Chat بين المستخدم والـ Admin، Reply داخل الموقع، Notifications، أو تصنيفات للرسائل — وذلك بناءً على متطلبات الـ MVP البسيط.
#   a n o n y m o u s - q u e s t i o n s - b o x  
 