# 🎬 GitHappens - BLG317E Project

## 👥 Team Members
- Faruk Yiğit Oluşan (farukyo)
- Turgut Emre Sürenkök (T-Emre-S)
- Ceyda Nur Akalın (cedaynur)
- Eylül Ebrar Gülbeyaz (eylulebrar)
- Şevval Hayyar (sevvaaal)

## 🎓 Teaching Assistant (TA)
- Elif Yıldırım

---

## 🌐 Web Design & Features

- **Home Page**: Landing page of the application.
- **Movies Page**: Shows all movies fetched from the database and provides navigation to individual movie detail pages.
- **Series Page**: Lists series, connected to episodes.
- **Episodes Page**: Includes a search section with filters. Clicking an episode directs the user to a detail page.
- **Celebrities Page**:
    - **Search Bar**: Search for anything related to the people table.
    - **Filters**: Create queries in people and profession tables.
    - Detail page for celebrities (Planned).
- **Recommend Page** (Requires Login): Recommends movies, series, or celebrities based on user likes.
- **Quizzes Page** (Requires Login): Asks random funny questions about chosen topics.
- **About Page**: Information about the team and project.
- **Suggestion Page** (Requires Login): Users can send messages/suggestions (DB or mail connection).
- **Login - Signup Pages**: User authentication.
- **User Page**:
    - Holds user information.
    - Lists liked movies, series, celebrities, episodes.
    - Displays quiz scores.

---

## 📁 Project Structure

This guide is for developers who want to contribute to the project.

```text
├── main.py                 # Main entry point to start the app
├── requirements.txt        # Python dependencies
│
├── routes/                 # Page routing logic (URLs)
│   ├── main_routes.py      # Home, about, quiz, suggestion
│   ├── auth_routes.py      # Login, signup, logout + User model
│   ├── user_routes.py      # User profile
│   ├── movie_routes.py     # Movie list and details
│   ├── series_routes.py    # Series list
│   ├── episode_routes.py   # Episode list and details
│   └── celebrity_routes.py # Celebrity list
│
├── templates/              # HTML Templates
│   ├── base.html           # Common template (navbar, footer)
│   ├── home.html           # Home page
│   ├── movies.html         # Movies list
│   ├── movie.html          # Movie detail
│   ├── series.html         # Series list
│   ├── episodes.html       # Episodes list
│   ├── episode.html        # Episode detail
│   ├── celebrities.html    # Celebrities list
│   ├── login.html          # Login page
│   ├── signup.html         # Signup page
│   ├── profile.html        # User profile
│   └── ...                 # Other pages
│
├── static/                 # Static files
│   ├── css/                # Stylesheets
│   │   ├── base.css        # General styles
│   │   ├── home.css        # Home page styles
│   │   ├── movies.css      # Movies page styles
│   │   └── ...             # Individual page styles
│   ├── js/                 # JavaScript files
│   └── img/                # Images
│
├── database/               # Database connection
│   └── db.py               # MySQL connection settings
│
├── admin/                  # Admin panel
│   ├── routes.py           # Admin routes
│   └── admin.py            # Admin operations
│
├── data/                   # CSV data files
└── sql/                    # SQL query files
```

---

## 🔧 Developer Guide

### 🎨 Changing Page Appearance (HTML)
Go to the `templates/` folder.
- **Home**: `templates/home.html`
- **Movies**: `templates/movies.html`
- **Movie Detail**: `templates/movie.html`
- **Navbar/Footer**: `templates/base.html` (Common for all pages)

### 🎭 Changing Styles (CSS)
Go to the `static/css/` folder.
- `base.css`: General styles, navbar, footer.
- `home.css`: Home page specific styles.
- `movies.css`: Movies page specific styles.

### ⚙️ Changing Data Logic (Python/Routes)
Go to the `routes/` folder.
- **Movies/Search/Filter**: `routes/movie_routes.py`
- **Series**: `routes/series_routes.py`
- **Episodes**: `routes/episode_routes.py`
- **Celebrities**: `routes/celebrity_routes.py`
- **Auth (Login/Signup)**: `routes/auth_routes.py`
- **Home/Quiz/Suggestion**: `routes/main_routes.py`
- **User Profile**: `routes/user_routes.py`

### 👤 Modifying User Model
Open `routes/auth_routes.py`. The `User` class contains fields like:
- username, email, password
- dob (date of birth), gender
- liked_movies, liked_series, liked_actors

### 🗄️ Database Connection
Open `database/db.py` to modify MySQL connection settings.

### 🛠️ Admin Panel
- Routes: `admin/routes.py`
- Templates: `templates/admin/`

### ➕ Adding a New Page
1. Add a new route in the appropriate file in `routes/` (or create a new file).
2. Create a new HTML file in `templates/`.
3. (Optional) Add a CSS file in `static/css/`.
4. If you created a new route file, register it in `routes/__init__.py` and `main.py`.

---

## 🚀 How to Run

---

### 🗄️ Database Setup

To set up the database, execute the files in the `sql/` folder in the following order:

1. **`userdb.sql`**: Creates the user database (`githappens_users`) and its tables.
2. **`genres.sql`**: Creates the `genres` table and loads data.
3. **`all_titles.sql`**: Creates the `all_titles` parent table.
4. **`movies.sql`**: Creates the `movies` table and links it with `genres`.
5. **`series.sql`**: Creates the `series` table and links it with `genres`.
6. **`episodes.sql`**: Creates the `Episode` table.
7. **`names.sql`**: Creates the `people` and `profession` tables.
8. **`professionnormalization.sql`**: Normalizes profession data (parses and links).
9. **`ratings.sql`**: Creates the `ratings` table.
10. **`principals.sql`**: Creates the `principals` table (relationship between titles and people).
11. **`addnewadmin.sql`**: Adds a default admin user to the system.

**Important Note:** For data loading operations, you may need to enable the `local_infile` setting in MySQL and increase the timeout duration.

---

## 🔑 API Setup

Before running the application, you need to set up the Groq API key for AI-powered features.

### Step 1: Create Groq API Key
1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign in with your email
3. Click "Create API Key"
4. Set project name to: `githappens`
5. Select duration (e.g., 1 month)
6. Copy the generated API key (keep it safe, don't lose it)

### Step 2: Configure Environment Variable
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file and replace the placeholder values with your actual credentials:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   ```

---

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start the application
python main.py
```

Open in browser: `http://localhost:8080`

---
