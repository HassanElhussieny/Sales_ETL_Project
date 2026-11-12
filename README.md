# 🔄 Sales ETL Pipeline — Zero to Hero

A professional, production-ready ETL (Extract, Transform, Load) pipeline built with Python and PostgreSQL. Automatically discovers, cleans, and loads Excel sales data into a relational database — with email alerts and scheduling support.

---

## 📁 Project Structure

```
Sales_ETL_Project/
│
├── config/
│   ├── __init__.py
│   ├── settings.py       # All project settings in one place
│   └── .env              # Your credentials — create locally, never committed (see step 5)
│
├── data/
│   ├── sales_2013.xlsx   # Raw sales data — drop any new year here!
│   └── sales_2014.xlsx
│
├── logs/                 # Created automatically on first run (git-ignored)
│   └── pipeline.log      # Run history
│
├── main/
│   ├── __init__.py
│   ├── logger.py         # Logging to terminal + file
│   ├── extract.py        # Auto-discovers and reads Excel files
│   ├── transform.py      # Cleans, standardizes, and validates data
│   ├── load.py           # Loads clean data into PostgreSQL
│   └── notifier.py       # Sends Gmail alerts on success or failure
│
├── scripts/
│   ├── __init__.py
│   └── pipeline.py       # Orchestrates the full ETL flow
│
├── run_pipeline.bat      # Windows batch file for Task Scheduler (location-independent)
├── requirements.txt      # Pinned Python dependencies
├── .gitignore
├── .gitattributes        # Line-ending rules
└── README.md             # You are here!
```

---

## ⚙️ How It Works

```
Excel Files (data/)
      ↓
[ EXTRACT ]  — Auto-discovers all .xlsx files, reads and stacks them
      ↓
[ TRANSFORM ] — Standardizes columns, fixes types, handles nulls, removes duplicates
      ↓
[ LOAD ]     — Pushes clean data into PostgreSQL with verification
      ↓
[ NOTIFY ]   — Sends Gmail email with full summary report
      ↓
PostgreSQL (sales_db → sales table)
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/HassanElhussieny/Sales_ETL_Project.git
cd Sales_ETL_Project
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
- Create a database called `sales_db`
- Note your host, port, username, and password

### 5. Configure your environment
Create `config/.env` with your credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_NAME=sales_db

EMAIL_SENDER=yourgmail@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=yourgmail@gmail.com
```

> ⚠️ Never commit `.env` to Git — it contains your secrets!

### 6. Add your data files
Drop your Excel files into the `data/` folder:
```
data/
  sales_2013.xlsx
  sales_2014.xlsx
  sales_2015.xlsx   ← just drop it in, pipeline picks it up automatically!
```

### 7. Run the pipeline
```bash
python scripts\pipeline.py
```

The script exits with code `0` on success and `1` on failure, so Windows Task Scheduler's "Last Run Result" shows failed runs correctly.

### 8. Run the tests (optional)
```bash
pip install pytest
python -m pytest tests
```
The tests run fully offline: the database, email and data steps are replaced with fakes.

---

## 📦 Requirements

Main libraries (exact versions are pinned in `requirements.txt`):
```
pandas
openpyxl
sqlalchemy
psycopg2-binary
python-dotenv
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Auto-discovery** | Drop any new Excel file in `data/` — pipeline picks it up automatically |
| **Flexible columns** | Handles column name differences between files (e.g. "Discount" vs "Discounts") |
| **Data validation** | Fills nulls, drops invalid rows, removes duplicates |
| **Professional logging** | Every run logged to terminal AND `logs/pipeline.log` |
| **Email alerts** | Gmail notification on success or failure with full summary |
| **Scheduling** | Runs automatically via Windows Task Scheduler |
| **Power BI ready** | Connect Power BI directly to PostgreSQL for live dashboards |

---

## 📊 Data Transformations Applied

- Column name standardization (snake_case)
- Leading/trailing whitespace removal
- Duplicate column detection and removal
- Numeric type enforcement
- Date parsing to proper timestamps
- Null filling for non-critical fields
- Row dropping for missing required fields
- Duplicate row removal
- Audit columns added to every row: `source_file` (origin Excel file) and `loaded_at` (load timestamp)

Rows are loaded in **append** mode (`LOAD_MODE` in `config/settings.py`), so running the pipeline again on the same files adds the rows again.

---

## 🗄️ Database Schema

Table: `sales`

| Column | Type | Description |
|---|---|---|
| segment | text | Customer segment |
| country | text | Country of sale |
| product | text | Product name |
| discount_band | text | Discount tier |
| units_sold | numeric | Number of units sold |
| manufacturing_price | numeric | Cost to manufacture |
| sale_price | numeric | Price sold at |
| gross_sales | numeric | Total gross sales |
| discount | numeric | Discount amount |
| sales | numeric | Net sales |
| cogs | numeric | Cost of goods sold |
| profit | numeric | Net profit |
| date | timestamp | Sale date |
| month_number | numeric | Month number |
| month_name | text | Month name |
| year | numeric | Year |
| source_file | text | Source Excel filename |
| loaded_at | timestamp | When row was loaded by pipeline |

---

## 📧 Email Alerts

The pipeline automatically sends emails via Gmail:

**On success:**
```
Subject: ✅ ETL Pipeline — Completed Successfully
Body: Summary with rows extracted, loaded, dropped, and total time
```

**On failure:**
```
Subject: ❌ ETL Pipeline — FAILED
Body: Full error traceback + path to log file
```

---

## ⏰ Scheduling (Windows)

Use `run_pipeline.bat` with Windows Task Scheduler to run automatically:
1. Open Task Scheduler → Create Basic Task
2. Set your preferred schedule (daily, hourly, etc.)
3. Action: Start `run_pipeline.bat`
4. Done — pipeline runs automatically!

`run_pipeline.bat` uses paths relative to its own folder, so it works wherever the project is cloned. It activates `venv\` if present, otherwise it uses the Python on your PATH.

---

## 🔗 Connect to Power BI

1. Open Power BI Desktop
2. Get Data → PostgreSQL
3. Server: `localhost` | Database: `sales_db`
4. Select the `sales` table → Load
5. Build your dashboards on clean, live data!

---

## 👨‍💻 Author

**Hassan Elhussieny**
Data Analyst
[LinkedIn](https://www.linkedin.com/in/hassan-elhussieny-023291273/) | [GitHub](https://github.com/HassanElhussieny)

---

## 📄 License

MIT License — feel free to use, modify, and share!
