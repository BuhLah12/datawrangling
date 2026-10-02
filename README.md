# Data Wrangling & Analisis Performa Retail

Project ini merupakan implementasi **data wrangling dan integrasi data** dari beberapa sumber untuk menghasilkan dataset master yang siap dianalisis dan divisualisasikan.

Proses utama menggabungkan:

- Data transaksi dalam format CSV.
- Data pelanggan/CRM dari PostgreSQL.
- Data logistik dalam format JSON, dengan opsi mengambil data dari sumber online dan fallback ke file lokal.
- Validasi kualitas data dan pembuatan data dictionary.
- Visualisasi ringkasan performa kampanye kupon dan logistik.

## Tujuan Project

Project ini bertujuan untuk:

1. Mengintegrasikan data transaksi, pelanggan, dan logistik.
2. Membersihkan dan menghilangkan duplikasi berdasarkan `order_id`.
3. Memastikan data hasil integrasi memenuhi aturan validasi dasar.
4. Membuat data dictionary secara otomatis.
5. Menghasilkan visualisasi ringkasan untuk membantu analisis performa transaksi, pelanggan, kupon, dan pengiriman.

## Struktur File

```text
.
├── generate_csv.py
├── generate_json.py
├── setup_db.py
├── transaksi.csv
├── data_logistik.json
├── kamus_data.csv
├── yyyyy.ipynb
└── dashboard_performa_retail.png
```

### Penjelasan File

| File | Keterangan |
|---|---|
| `generate_csv.py` | Script untuk membuat 10.000 data transaksi secara sintetis dan menyimpannya sebagai `transaksi.csv`. |
| `generate_json.py` | Script untuk membuat 10.000 data logistik sintetis dalam format JSON. |
| `setup_db.py` | Script untuk membuat tabel `customers` pada PostgreSQL menggunakan data pelanggan sintetis. |
| `transaksi.csv` | Dataset transaksi yang berisi `order_id`, `customer_id`, `order_date`, `total_amount`, dan `coupon_code`. |
| `data_logistik.json` | Dataset logistik yang berisi nomor pesanan, nomor tracking, dan status pengiriman. |
| `kamus_data.csv` | Data dictionary hasil proses integrasi dan validasi. |
| `yyyyy.ipynb` | Notebook utama untuk loading data, integrasi, validasi, pembuatan data dictionary, dan visualisasi. |
| `dashboard_performa_retail.png` | Hasil visualisasi ringkasan eksekutif. |

## Alur Data

```text
                     ┌──────────────────┐
                     │  transaksi.csv   │
                     └────────┬─────────┘
                              │
                              │ customer_id
                              ▼
                     ┌──────────────────┐
                     │ PostgreSQL / CRM │
                     │    customers     │
                     └────────┬─────────┘
                              │
                              │
                              ▼
                     ┌──────────────────┐
                     │ Integrasi Data   │
                     │      Master      │
                     └────────┬─────────┘
                              ▲
                              │ order_id
                     ┌────────┴─────────┐
                     │ data_logistik    │
                     │      JSON        │
                     └──────────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │ Cleaning & Data Validation│
                └────────────┬─────────────┘
                             │
                ┌────────────┴─────────────┐
                ▼                          ▼
        ┌────────────────┐       ┌────────────────────┐
        │kamus_data.csv  │       │ Visualisasi/Output │
        └────────────────┘       └────────────────────┘
```

## Dataset

### 1. Data Transaksi

`transaksi.csv` berisi data transaksi dengan kolom:

| Kolom | Deskripsi |
|---|---|
| `order_id` | ID unik transaksi/pesanan |
| `customer_id` | ID pelanggan |
| `order_date` | Tanggal transaksi |
| `total_amount` | Nilai transaksi |
| `coupon_code` | Kode kupon yang digunakan |

Data transaksi dibuat secara sintetis menggunakan `generate_csv.py`.

### 2. Data Customer/CRM

Data customer disimpan pada PostgreSQL dalam tabel `customers`.

Kolom yang dibuat oleh `setup_db.py`:

| Kolom | Deskripsi |
|---|---|
| `customer_id` | ID pelanggan |
| `customer_name` | Nama pelanggan |
| `membership_tier` | Tingkatan membership: Bronze, Silver, Gold, atau Platinum |
| `city` | Kota pelanggan |
| `is_active` | Status aktif pelanggan |

Pada notebook, hanya pelanggan dengan:

```sql
WHERE is_active = 1
```

yang digunakan dalam proses integrasi.

### 3. Data Logistik

`data_logistik.json` memiliki struktur utama:

```json
{
  "results": [
    {
      "order_id": "ORD00001",
      "tracking_number": "LOG-00001-ID",
      "delivery_status": "DELIVERED"
    }
  ]
}
```

Status pengiriman yang digunakan:

- `DELIVERED`
- `PENDING`
- `CANCELLED`
- `RETURNED`

## Proses Data Wrangling

### 1. Load Data Transaksi

Data transaksi dibaca menggunakan Pandas dan `order_date` dikonversi menjadi tipe tanggal.

```python
df = pd.read_csv(
    'transaksi.csv',
    dtype={'customer_id': str},
    parse_dates=['order_date']
)
```

### 2. Load Data CRM

Data customer diambil dari PostgreSQL menggunakan SQLAlchemy.

Database yang digunakan oleh script:

```text
PostgreSQL
Database : data_wringling
User     : postgres
Password : pw
Host     : localhost
Port     : 5432
```

Query hanya mengambil customer aktif.

### 3. Load Data Logistik

Notebook mencoba mengambil data logistik dari sumber online. Jika sumber online tidak dapat diakses, notebook menggunakan `data_logistik.json` lokal.

Sumber online yang digunakan pada notebook:

```text
https://gist.githubusercontent.com/BuhLah12/1ceb42f12fa973cbb3e3be2770c8c541/raw/3ce25c3087df2798630aa014001c2961b7eb1558/data_logistik.json
```

### 4. Menghapus Duplikasi

Data logistik dibersihkan berdasarkan `order_id`:

```python
df_logistik = df_logistik.drop_duplicates(
    subset=['order_id'],
    keep='last'
)
```

Data master juga kembali diperiksa untuk memastikan satu `order_id` hanya muncul satu kali.

### 5. Integrasi Data

Integrasi dilakukan dengan dua jenis join:

```python
df_master = (
    df
    .merge(df_crm, how='inner', on='customer_id')
    .merge(df_logistik, how='left', on='order_id')
)
```

Artinya:

- Transaksi dan customer digabung menggunakan **inner join** berdasarkan `customer_id`.
- Data logistik digabung menggunakan **left join** berdasarkan `order_id`.

Hasil akhirnya disimpan dalam DataFrame `df_master`.

## Validasi Data

Notebook melakukan beberapa validasi menggunakan `assert`.

### Keunikan Order

```python
assert df_master['order_id'].is_unique
```

Memastikan tidak terdapat `order_id` yang duplikat.

### Nilai Transaksi

```python
assert (df_master['total_amount'] >= 0).all()
```

Memastikan nilai transaksi tidak negatif.

### Tanggal Transaksi

```python
assert (
    df_master[df_master['order_date'] <= dt.datetime.now()].shape[0]
    == df_master.shape[0]
)
```

Memastikan tidak terdapat tanggal transaksi di masa depan.

Berdasarkan `kamus_data.csv`, hasil integrasi yang digunakan pada output memiliki **4.915 record** dan tidak menunjukkan missing value pada kolom-kolom yang tercantum.

## Data Dictionary

`kamus_data.csv` dibuat secara otomatis dari `df_master`.

Informasi yang dicatat untuk setiap kolom:

- Nama kolom.
- Tipe data.
- Jumlah missing value.
- Jumlah nilai unik.
- Contoh nilai.

Contoh:

```text
Nama Kolom     : order_id
Tipe Data      : str
Missing Values : 0
Jumlah Unik    : 4915
```

## Visualisasi

Notebook menghasilkan file:

```text
<img width="4781" height="3430" alt="dashboard_performa_retail" src="https://github.com/user-attachments/assets/054fcd88-96a1-4dbc-8b4c-de9a872b9943" />

```

Visualisasi terdiri dari empat bagian:

### 1. Penggunaan Kupon Diskon

Menampilkan jumlah transaksi berdasarkan kode kupon.

Pada output yang tersedia:

- `NONE`: 2.631 transaksi
- `DISC 50`: 891 transaksi
- `DISCC20`: 710 transaksi
- `DISC10`: 683 transaksi

### 2. Profil Membership Customer

Menampilkan proporsi customer berdasarkan membership tier:

- Bronze: 26,0%
- Platinum: 24,8%
- Gold: 24,7%
- Silver: 24,5%

### 3. Status Pengiriman

Menampilkan distribusi status pengiriman:

- `DELIVERED`: 3.424 pesanan
- `PENDING`: 993 pesanan
- `RETURNED`: 261 pesanan
- `CANCELLED`: 237 pesanan

### 4. Total Transaksi berdasarkan Membership dan Kupon

Menampilkan total nilai transaksi berdasarkan kombinasi:

- Membership tier.
- Coupon code.

Visualisasi ini dapat digunakan untuk melihat pola nilai transaksi pada setiap kelompok membership dan penggunaan kupon.

## Instalasi dan Persiapan Environment

Disarankan menggunakan Python 3.9+.

Install library yang diperlukan:

```bash
pip install pandas numpy sqlalchemy psycopg2-binary faker matplotlib seaborn requests jupyter
```

Jika menggunakan Jupyter Notebook:

```bash
jupyter notebook
```

## Persiapan PostgreSQL

Pastikan PostgreSQL sudah aktif dan database berikut tersedia:

```text
data_wringling
```

Sesuaikan konfigurasi koneksi pada `setup_db.py` dan `yyyyy.ipynb` jika username, password, host, port, atau nama database berbeda.

Default yang digunakan project:

```text
postgresql://postgres:pw@localhost:5432/data_wringling
```

Kemudian jalankan:

```bash
python setup_db.py
```

Script tersebut akan membuat/mengganti tabel:

```text
customers
```

dengan 10.000 data customer sintetis.

## Menjalankan Project

Urutan pengerjaan yang direkomendasikan:

### 1. Membuat data transaksi

```bash
python generate_csv.py
```

Output:

```text
transaksi.csv
```

### 2. Membuat data logistik

```bash
python generate_json.py
```

Output:

```text
data_logistik.json
```

### 3. Menyiapkan data customer di PostgreSQL

Pastikan database sudah tersedia, kemudian:

```bash
python setup_db.py
```

### 4. Menjalankan notebook

Buka:

```text
yyyyy.ipynb
```

Jalankan cell secara berurutan.

Notebook akan:

1. Membaca transaksi.
2. Mengambil data customer aktif dari PostgreSQL.
3. Mengambil data logistik dari sumber online atau file lokal.
4. Melakukan integrasi.
5. Menghapus duplikasi.
6. Melakukan validasi.
7. Membuat `kamus_data.csv`.
8. Membuat `dashboard_performa_retail.png`.

## Catatan Teknis

### Import `requests`

Notebook menggunakan:

```python
requests.get(...)
```

untuk mengambil data logistik dari sumber online. Pastikan library `requests` sudah terpasang dan tambahkan import berikut pada bagian awal notebook jika belum tersedia:

```python
import requests
```

### Data Sintetis

Data pada project dibuat secara sintetis menggunakan library `Faker` dan `random`. Oleh karena itu, data tidak merepresentasikan transaksi pelanggan atau perusahaan nyata.

### Random Seed

Beberapa script menggunakan seed:

```python
Faker.seed(42)
random.seed(42)
```

Hal ini membantu menghasilkan data sintetis yang lebih konsisten ketika script dijalankan kembali.

## Output Utama

Setelah seluruh proses selesai, output utama project adalah:

```text
kamus_data.csv
dashboard_performa_retail.png
```

`kamus_data.csv` digunakan sebagai dokumentasi struktur dan kualitas dataset hasil integrasi, sedangkan `dashboard_performa_retail.png` digunakan sebagai ringkasan visual performa transaksi, membership, kupon, dan logistik.

## Ringkasan

Project ini menunjukkan proses **end-to-end data wrangling**, mulai dari pembuatan dan pengambilan data dari beberapa sumber, integrasi menggunakan key yang berbeda, pembersihan dan validasi data, hingga penyusunan data dictionary dan visualisasi.

Dengan pendekatan tersebut, data transaksi, customer, dan logistik dapat disatukan menjadi dataset master yang lebih siap digunakan untuk analisis performa retail.
