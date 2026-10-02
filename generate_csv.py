import pandas as pd
from faker import Faker
import random
from datetime import datetime,timedelta

fake = Faker('id_ID')
random.seed(42)

print("[INFO] Membuat tabel customers dengan 10.000 data di PostgreSQL...")

coupons = ['DISC10', 'DISCC20','DISC 50','NONE','NONE','NONE']
data_transaksi = []
start_time = datetime(2026,1,1)
end_time = datetime.now()
max_days = (end_time - start_time).days

for i in range(1,10001):
    random_days = random.randint(0, max_days)
    order_date = start_time + timedelta(days=random_days)

    data_transaksi.append({
        'order_id': f'ORD{i:05d}',
        'customer_id': f'CUST{random.randint(1, 10000):05d}',
        'name': f'{fake.firts_name()}{fake.last_name()}',
        'order_date': order_date.strftime('%Y-%m-%d'),
        'total_amount': random.randint(25, 1000)*1000,
        'coupon_code': random.choice(coupons)
    })

    df_transaksi = pd.DataFrame(data_transaksi)
    df_transaksi.to_csv('transaksi.csv', index=False)
    print("[INFO] Berhasil membuat file transaksi.csv dengan 10.000 data transaksi!")

