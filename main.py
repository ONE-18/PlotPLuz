import requests
import plotext as plt
from datetime import date, datetime
import os

def obtener_precios_luz(url):
    response = requests.get(url)
    if response.status_code == 200:
        guardar_respuesta(response.text)
        return response.json()
    else:
        print("Error al obtener los datos _ luz")
        return None

def procesar_datos(data):
    horas = []
    precios = []
    cheap = []
    under_avg = []
    date = None
    units = None

    precios_undr = []
    precios_over = []
    precios_cheap = []

    for hour_range, details in data.items():
        date = details.get('date')
        hour = details.get('hour')
        is_cheap = details.get('is-cheap')
        is_under_avg = details.get('is-under-avg')
        market = details.get('market')
        price = details.get('price')
        units = details.get('units')

        horas.append(hour.split('-')[0])
        precios.append(price)
        cheap.append(is_cheap)
        under_avg.append(is_under_avg)
        date = date
        units = units

        if is_under_avg:
            if is_cheap:
                precios_cheap.append(price)
                precios_undr.append(0)
                precios_over.append(0)
            else:
                precios_undr.append(price)
                precios_over.append(0)
                precios_cheap.append(0)
        else:
            precios_over.append(price)
            precios_undr.append(0)
            precios_cheap.append(0)


    return horas, precios, cheap, under_avg, date, units, precios_undr, precios_over, precios_cheap

def mostrar_grafico(horas, precios, dates, unit, cheap, under_avg, precios_undr, precios_over, precios_cheap):
    media = sum(precios) / len(precios)
    """Función para crear y mostrar el gráfico en la terminal usando plotext."""
    # plt.clear_terminal() # Limpiamos cualquier gráfico anterior
    plt.stacked_bar(horas, [precios_undr, precios_over, precios_cheap], color=['orange', 'red', 'green'], fill=True, width = 3/5, label=['Baratos', 'Caros', 'Más baratos'])
    plt.title('Precios de la luz por hora - ' + dates)
    plt.xlabel('Hora')
    plt.ylabel('Precio (' + unit + ')')
    plt.grid(True)      # plt.theme('matrix')
    plt.theme('pro')
    plt.vertical_line(datetime.now().hour+1, 190)
    plt.horizontal_line(media, "blue")
    plt.show()

def imprimir_tramos_continuos(tipo, horas, precios_cheap, unit):
    tramos_continuos = []
    tramo_actual = []

    for i, precio in enumerate(precios_cheap):
        if precio:
            tramo_actual.append((horas[i], precio))
        else:
            if tramo_actual:
                tramos_continuos.append(tramo_actual)
                tramo_actual = []

    if tramo_actual:
        tramos_continuos.append(tramo_actual)

    print(f"\nPrecios {tipo}:")
    for tramo in tramos_continuos:
        horas_tramo = [hora for hora, _ in tramo]
        precios_tramo = [precio for _, precio in tramo]
        hora_prim = horas_tramo[0]
        hora_ulti = f"{int(horas_tramo[-1])+1}"
        if len(hora_ulti) == 1:
            hora_ulti = "0" + hora_ulti
        precio_min = min(precios_tramo)
        precio_max = max(precios_tramo)
        print(f"{hora_prim} - {hora_ulti}: {precio_min} - {precio_max} {unit}")

def guardar_respuesta(data):
    if not os.path.exists("historico"):
        os.makedirs("historico")
    nombre_archivo = f"historico/respuesta_{date.today()}.json"
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "w") as file:
            file.write(data)

def main():
    url = 'https://api.preciodelaluz.org/v1/prices/all?zone=PCB'
    data = obtener_precios_luz(url)
    if data:
        horas, precios, cheap, und_avg, date, unit, precios_undr, precios_over, precios_cheap = procesar_datos(data)
        mostrar_grafico(horas, precios, date, unit, cheap, und_avg, precios_undr, precios_over, precios_cheap)
        imprimir_tramos_continuos("más baratos", horas, precios_cheap, unit)
        imprimir_tramos_continuos("baratos", horas, precios_undr, unit)
        imprimir_tramos_continuos("caros", horas, precios_over, unit)
        print(f"\nPrecio medio:\n{round(sum(precios) / len(precios),2)} {unit}")
        print(f"\nPrecio actual:\n{precios[datetime.now().hour]} {unit}")

if __name__ == "__main__":
    main()
