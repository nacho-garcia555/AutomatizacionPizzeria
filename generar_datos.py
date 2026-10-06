import random
import pandas as pd

random.seed(42)
PRECIOS = {"Margarita": 9.5, "Pepperoni": 11.0, "Cuatro quesos": 12.5,
           "Barbacoa": 12.0, "Hawaiana": 10.5}

filas = []
for dia in pd.date_range(end=pd.Timestamp.today().normalize(), periods=30):
    for _ in range(random.randint(15, 40)):
        producto = random.choice(list(PRECIOS))
        filas.append({"fecha": dia.date(), "producto": producto,
                      "precio": PRECIOS[producto],
                      "cantidad": random.randint(1, 4)})

pd.DataFrame(filas).to_csv("pedidos.csv", index=False)
print(f"pedidos.csv generado con {len(filas)} filas")