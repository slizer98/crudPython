from flask import Flask
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory
import os

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'clasepython'
app.config['MYSQL_DATABASE_Host'] = 'localhost'
mysql.init_app(app)
#mysql = MySQL(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/')
    #, methods =['GET', 'POST'])
def index():
    sql = "SELECT * FROM `empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    empleados = cursor.fetchall()

    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)
@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    now =datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if _foto.filename != '':
        nuevoNombre = tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombre)


    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES(NULL, %s, %s, %s)"
    datos = (_nombre, _correo, nuevoNombre)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')

@app.route('/destroy/<int:id>')
def destroy (id) :
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id=%s", id)
    conn.commit()
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados = cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtId']

    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s;"

    datos = (_nombre, _correo, id)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    now = datetime.now()
    hora = now.strftime('%Y%H%M%S')

    if _foto.filename != '':
        nuevoNombre = hora+_foto.filename
        _foto.save('uploads/'+nuevoNombre)
        cursor.execute("SELECT foto FROM empleados WHERE id = %s", id)
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE empleados SET foto = %s WHERE id = %s", (nuevoNombre, id))
        conn.commit()

    return redirect('/')

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

if __name__ == '__main__':
    #app.run()
    app.run(debug=True)