import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

import pandas as pd

ENTRADA = Path("pedidos.csv")
SALIDA = Path("informe_ventas.xlsx")


# 1. Entrada
def leer() -> pd.DataFrame:
    df = pd.read_csv(ENTRADA, parse_dates=["fecha"]).dropna()
    df = df[(df["cantidad"] > 0) & (df["precio"] > 0)]
    df["total"] = df["cantidad"] * df["precio"]
    return df


# 2. Procesar
def procesar(df: pd.DataFrame):
    por_dia = (df.groupby(df["fecha"].dt.date)["total"]
                 .sum().reset_index(name="ventas"))
    por_dia.columns = ["fecha", "ventas"]
    por_producto = (df.groupby("producto")
                      .agg(unidades=("cantidad", "sum"), ventas=("total", "sum"))
                      .sort_values("ventas", ascending=False)
                      .reset_index())
    return por_dia, por_producto


# 3. Salida
def escribir(por_dia: pd.DataFrame, por_producto: pd.DataFrame) -> None:
    with pd.ExcelWriter(SALIDA, engine="openpyxl") as w:
        for nombre, tabla in (("Ventas por día", por_dia),
                              ("Por producto", por_producto)):
            tabla.to_excel(w, sheet_name=nombre, index=False)
            hoja = w.sheets[nombre]
            for col in hoja.columns:
                ancho = max(len(str(c.value)) for c in col) + 3
                hoja.column_dimensions[col[0].column_letter].width = ancho


def enviar(resumen: str) -> None:
    usuario = os.environ.get("SMTP_USER")
    clave = os.environ.get("SMTP_PASS")
    destino = os.environ.get("DESTINO")
    if not (usuario and clave and destino):
        print("Sin credenciales: email omitido.")
        return

    msg = EmailMessage()
    msg["Subject"] = "Informe de ventas"
    msg["From"] = usuario
    msg["To"] = destino
    msg.set_content(resumen)
    msg.add_attachment(SALIDA.read_bytes(), maintype="application",
                       subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       filename=SALIDA.name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(usuario, clave)
        s.send_message(msg)
    print("Email enviado.")


def main() -> None:
    df = leer()
    por_dia, por_producto = procesar(df)
    escribir(por_dia, por_producto)

    top = por_producto.iloc[0]
    resumen = (f"Ventas totales: {df['total'].sum():.2f} €\n"
               f"Producto más vendido: {top['producto']} "
               f"({top['unidades']} uds, {top['ventas']:.2f} €)")
    print(resumen)
    enviar(resumen)


if __name__ == "__main__":
    main()