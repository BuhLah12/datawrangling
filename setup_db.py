import pandas as pd
from sqlalchemy import create_engine
from faker import Faker
import random

db_url = 'postgresql://postgres:pw@localhost:5432/data_wringling'
engine = create_engine(db_url)

fake = Faker('id_ID')
Faker.seed(42)
random.seed(42)

print("[INFO] Membuat tabel customers dengan 10.000 data di PostgreSQL...")
data_customers = []
tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']

for _ in range(10000):
    customer = {
        "customer_id": f"CUST{random.randint(1, 10000):05d}",
        "customer_name": fake.name(),
        "membership_tier": random.choice(tiers),
        "city": fake.city_name(),
        "is_active": random.choice([0, 1])
    }
    data_customers.append(customer)

df_customers = pd.DataFrame(data_customers)
df_customers.to_sql("customers", con=engine, if_exists="replace", index=False)
print("[INFO] Berhasil membuat tabel customers dengan 10.000 data di PostgreSQL!")