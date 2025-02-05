from flask import Flask, request, jsonify, send_from_directory
import csv
import os
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)

# Asegurar que el archivo CSV existe
CSV_FILE = "respuestas.csv"
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nombre", "Edad", "Opinión"])

# Crear la carpeta 'static' si no existe
if not os.path.exists("static"):
    os.makedirs("static")

# Clave secreta para proteger la gráfica
SECRET_KEY = "mi_clave_secreta"

# Ruta para servir el formulario
@app.route("/")
def serve_form():
    return send_from_directory("templates", "form.html")

# Ruta para guardar las respuestas del formulario
@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    age = request.form["age"]
    opinion = request.form["opinion"]

    # Guardar respuesta en el CSV
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, age, opinion])

    # Generar la gráfica después de guardar las respuestas
    generate_graph()

    return jsonify({"message": "Respuesta guardada correctamente."})

# Función para generar la gráfica
def generate_graph():
    # Intentar leer el archivo CSV con distintas codificaciones
    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(CSV_FILE, encoding='ISO-8859-1')
        except UnicodeDecodeError:
            df = pd.read_csv(CSV_FILE, encoding='latin1')

    print("Datos cargados para la gráfica:")
    print(df)

    # Graficar edades
    plt.figure(figsize=(8, 5))
    df["Edad"].plot(kind="hist", bins=10, color="skyblue", edgecolor="black")
    plt.xlabel("Edad")
    plt.ylabel("Frecuencia")
    plt.title("Distribución de Edades en la Encuesta")
    plt.savefig("static/graph.png")
    print("Gráfica guardada como 'static/graph.png'")

# Ruta para mostrar la gráfica de las respuestas
@app.route("/view_graphs")
def view_graphs():
    password = request.args.get("password")
    if password != SECRET_KEY:
        return jsonify({"error": "Acceso no autorizado"}), 403

    # Regenerar la gráfica cada vez que se accede a ella
    generate_graph()

    return send_from_directory("static", "graph.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
