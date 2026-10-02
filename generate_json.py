import json
import random

print("[INFO] Membuat file data_logistik.json dengan 10.000 data di lokal...")

statuses = ['DELIVERED', 'PENDING', 'CANCELLED', 'RETURNED']
status_weights = [70, 20, 5, 5]  # 70% terkirim, 20% pending, 5% dibatalkan, 5% dikembalikan
data_logistik = {'results': []}

for i in range(1, 10001):
    data_logistik['results'].append({
        'order_id': f'ORD{i:05d}',
        'tracking_number': f'LOG-{i:05d}-ID',
        'delivery_status': random.choices(statuses, weights=status_weights)[0]
    })

with open('data_logistik.json', 'w') as f:
    json.dump(data_logistik, f, indent=2)

print("[INFO] Berhasil membuat file data_logistik.json dengan 10.000 data di lokal!")