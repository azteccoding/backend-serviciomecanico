from flask import Flask, render_template, url_for, request, redirect, jsonify
from random import randint, choices
from utilities.qr import GeneradorQR
from utilities.html2pdf import HTML2PDF
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps, ObjectId
import os
import datetime
import json
from dotenv import dotenv_values



############  Definiendo variables de conexion con la DB local ###########
mongoClient = MongoClient('localhost',27017)                            ##
clients = mongoClient.taller_mecanico.clients                                    ##
services = mongoClient.taller_mecanico.services

##############  DB Atlas    ###############################################
env = dotenv_values(".env")
db = MongoClient(env["MONGO_URI"])
orders = db.clientapi.clientes

try:
    db.server_info()
    print("Conectado con éxito a la base de datos en la nube :) ")
except ConnectionFailure:
    print("ConnectionFailure -> No se pudo conectar a DB en la nube :(")                          ##
##########################################################################


app = Flask(__name__)

# No es necesario si se obtiene IP con qr
# def obtener_ip():
#     GET_IP_CMD = 'hostname -I'
#     raw_ip = sub.check_output(GET_IP_CMD, shell=True).decode('utf8')
#     return raw_ip.split(' ')[0]

def actualizar_json_obj(id, json_obj, modo='a'):
    este_folder = "registros/ids/"
    ext = '.json'
    with open(este_folder + id + ext, modo) as f:
        f.write(json_obj)

def crear_id_aleatorio():
    fecha = datetime.datetime.now().strftime("%Y%m%d%H%M") #entrega 12 caracteres
    letras_azar = ''.join(choices(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'], k=2)) #entrega 2 caracteres
    num_azar = randint(100,999)
    return letras_azar + fecha + 'x' + str(num_azar)


@app.route('/registrar/nuevocliente', methods=["GET", "POST"])
def crear_nuevo():
    if request.method == "POST":
        id = crear_id_aleatorio()
        fecha = datetime.datetime.now().strftime("%Y/%m/%d")
        hora = datetime.datetime.now().strftime("%H:%M")
        json_obj = '{\n' + f'"controlHora":"{hora}",\n"controlFecha":"{fecha}",\n'
        actualizar_json_obj(id, json_obj, modo='w')
############ Guardando datos iniciales del servicio  ####################################
        result = services.insert_one({'id_registro': id, 'fecha': fecha, 'hora': hora}) #
        print("\nregistro de servicio creado\n")                                            #
#########################################################################################
        return render_template('datoscliente.html', id=id)
    return render_template('crearnuevo.html')


@app.route('/datoscliente', methods=["GET", "POST"])
def ingresar_datos_cliente():
    if request.method == "POST":
        id = request.form["localstorage-id"]
        cliente = {
        "nombre" : request.form['nombre'],
        "telefono" : request.form['telefono'],
        "direccion" : request.form['direccion'],
        "whatsApp" : bool(request.form.get('whats'))
        }
        json_obj = f'"id_registro":"{id}",\n"cliente":{json.dumps(cliente, ensure_ascii=False)},\n'
        actualizar_json_obj(id, json_obj)
##################    Guardando en la DB    #####################################
        result = clients.insert_one(cliente)                                    #
        services.update({'id_registro':id},{"$set":{'id_cliente':result.inserted_id}})
        print("\nDatos del cliente guardados exitosamente\n")
#################################################################################
        return render_template('datosauto.html',id=id)
    return render_template('nocreado.html')


@app.route('/datosauto', methods=["GET", "POST"])
def datosauto():
    if request.method == "POST":
        id = request.form["localstorage-id"]
        print("id: ",id)
        datos_auto = {
        "tipo" : request.form['tipo'],
        "marca" : request.form['marca'],
        "modelo" : request.form['modelo'],
        "placas" : request.form['placas'],
        "kilometraje": request.form['kilometraje']
        }
        json_obj = f'"datosAuto":{json.dumps(datos_auto)},\n'
        actualizar_json_obj(id, json_obj)
##################  Buscando e insertando en servicio ##############################
        services.update({'id_registro':id},{"$set":{"datosauto":datos_auto}})
        print("\nInserción datos de auto exitosa\n")
####################################################################################
        return render_template('inventariointerno.html', id=id)
    return render_template('nocreado.html')


@app.route('/inventariointerno', methods=['GET', 'POST'])
def inventariointerno():
    if request.method == "POST":
        id = request.form['localstorage-id']
        checks = ["tablero", "aire", "plumas", "radio", "bocinas", "encendedor", "retrovisor", "ceniceros", "cinturones", "botones", "manijas", "tapetes", "vestiduras"]
        valores_checks = {}
        for checkbtn in checks:
            valores_checks.update({checkbtn:bool(request.form.get(checkbtn))})
        json_obj = f'"interiorAuto":{json.dumps(valores_checks)},\n'
        actualizar_json_obj(id, json_obj)
##################  Buscando e insertando en servicio ##############################
        services.update({'id_registro':id},{"$set":{"inventario_interior": valores_checks}})
        print("\nInserción inventario interno exitosa\n")
####################################################################################
        return render_template('inventarioexterno.html', id=id)
    return render_template('nocreado.html')


@app.route('/inventarioexterno', methods=['GET', 'POST'])
def inventarioexterno():
    if request.method == "POST":
        id = request.form['localstorage-id']
        checks = ("luces", "antena", "espejos", "cristales", "llantas", "tapones", "molduras", "gasolina", "parrilla", "claxon")
        valores_checks = {}
        for checkbtn in checks:
            valores_checks.update({checkbtn:bool(request.form.get(checkbtn))})
        json_obj = f'"exteriorAuto":{json.dumps(valores_checks)},\n'
        actualizar_json_obj(id, json_obj)
##################  Buscando e insertando en servicio ##############################
        services.update({'id_registro':id},{"$set":{"inventario_exterior": valores_checks}})
        print("\nInserción inventario externo exitosa\n")
####################################################################################
        return render_template('gasolina.html', id=id)
    return render_template('nocreado.html')


@app.route('/gasolina', methods=['GET', 'POST'])
def gasolina():
    if request.method == "POST":
        id = request.form['localstorage-id']
        gasolina = request.form["gasolina"]
        checks = ("gato", "maneral", "llave-ruedas", "estuche", "triangulos", "refaccion", "extintor")
        valores_checks = {}
        for checkbtn in checks:
            valores_checks.update({checkbtn:bool(request.form.get(checkbtn))})
        json_obj = f'"gasolinaPorCentaje":{gasolina},\n"accesorios":{json.dumps(valores_checks)},\n'
        actualizar_json_obj(id, json_obj)
##################  Buscando e insertando en servicio ##############################
        services.update({'id_registro':id},{"$set":{"accesorios": valores_checks}})
        services.update({'id_registro':id},{"$set":{"gasolinaPorCentaje": gasolina}})
        print("\nInserción gasolina exitosa\n")
####################################################################################
        return render_template('componentes.html', id=id)
    return render_template('nocreado.html')


@app.route('/componentes', methods=['GET', 'POST'])
def componentes():
    if request.method == "POST":
        id = request.form['localstorage-id']
        comentarios = request.form['comentarios']
        fecha = datetime.datetime.now().strftime("%Y/%m/%d")
        hora = datetime.datetime.now().strftime("%H:%M")
        checks = ("claxon", "tapon-aceite", "tapon-radiador", "varilla-aceite", "filtro", "bateria")
        valores_checks = {}
        for checkbtn in checks:
            valores_checks.update({checkbtn:bool(request.form.get(checkbtn))})
        json_obj = f'"componentes":{json.dumps(valores_checks)},\n"comentarios":"{comentarios}",\n"fecha":"{fecha}",\n"hora":"{hora}"' + '\n}'
        actualizar_json_obj(id, json_obj)
##################  Buscando e insertando en servicio ##############################
        services.update({'id_registro':id},{"$set":{"componentes": valores_checks}})
        services.update({'id_registro':id},{"$set":{"comentarios": comentarios, "estatus": 0}})
        print("\nInserción de componentes exitosa\n")
        doc = services.find({'id_registro':id})

        # Objecto leer JSON
        pdf = HTML2PDF(id)

        try:
            pdf.generar_pdf()
        except:
            print("Error en generacion de PDF")
        try:
            os.system("start utilities/output.pdf")
        except:
            print("Error en apertura de PDF")
        return render_template('crearnuevo.html')
    return render_template('nocreado.html')

##################### Nuevas rutas creadas  ################################
@app.route("/busqueda/cliente",methods = ['GET','POST'])
def busqueda_cliente():
    if request.method == "POST":
        tipo = request.form['tipo']
        campo = request.form['campo']
        if tipo=="1":
            doc = clients.find({'telefono': campo})
        elif tipo=="2":
            doc = clients.find({'nombre':campo})
        elif tipo=="3":
            sub = services.find_one({'id_registro':campo},{'_id':0, 'id_cliente':1})
            doc = clients.find({'_id':sub['id_cliente']})
        elif tipo=="4":
            servicio = services.find_one({'datosauto.placas':campo})
            print(list(servicio))
            doc = clients.find({'_id':servicio['id_cliente']})
        if(doc.count()):
            return render_template("showclientes.html",mostrador=doc,habilitador="hidden")
        return render_template("busqueda.html",alerta = "/static/js/cliente_no_encontrado.js")
    return render_template("busqueda.html", alerta = "")


@app.route("/edicion",methods = ['GET','POST'])
def edicion_cliente():
    if request.method == "POST":
        _id = request.form['_id']
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        whats = bool(request.form.get('whats'))
        clients.update({"_id":ObjectId(_id)},{"nombre":nombre,"telefono":telefono,"direccion":direccion, "whatsApp":whats})
        doc = clients.find({"_id":ObjectId(_id)})
        return render_template("showclientes.html",mostrador=doc,habilitador="hidden")
    name = request.args.get('nombre')
    tel = request.args.get('telefono')
    direct = request.args.get('direccion')
    doc = clients.find({"nombre":name,"telefono": tel, "direccion":direct})
    return render_template("edicion.html",nombre=name,telefono=tel,direccion=direct,mostrador=doc)


@app.route('/<_id>/nuevoservicio', methods=["GET", "POST"])
def insertando_datos_cliente(_id):
    id = crear_id_aleatorio()
    fecha = datetime.datetime.now().strftime("%Y/%m/%d")
    hora = datetime.datetime.now().strftime("%H:%M")
    json_obj = '{\n' + f'"controlHora":"{hora}",\n"controlFecha":"{fecha}",\n'
    actualizar_json_obj(id, json_obj, modo='w')
    ############ Guardando datos iniciales del servicio  ####################################
    result = services.insert_one({'id_registro': id, 'fecha': fecha, 'hora': hora}) #
    print("\nregistro de servicio creado\n")
    print("id: ",id)
    result = clients.find({"_id": ObjectId(_id)})
    for doc in result:
        cliente = {
        "nombre" : doc['nombre'],
        "telefono" : doc['telefono'],
        "direccion" : doc['direccion'],
        "whatsApp" : doc['whatsApp']
        }
        _id =doc['_id']
    json_obj = f'"id_registro":"{id}",\n"cliente":{json.dumps(cliente, ensure_ascii=False)},\n'
    actualizar_json_obj(id, json_obj)
##################    Guardando en la DB    #####################################
    services.update({'id_registro':id},{"$set":{'id_cliente':_id}})
    print("\nDatos del cliente guardados exitosamente\n")
#################################################################################
    print("Registro de cliente creado")
    print("id: ",id)
    return render_template("datosauto.html", id=id)


@app.route('/<_id>/historial')
def consulta_historial(_id):
    doc = services.find({"id_cliente":ObjectId(_id)})
    datos = clients.find({"_id":ObjectId(_id)})
    return render_template("showservicios.html",mostrador=doc, datos=datos)


@app.route('/')
def direccionar_status():
    return render_template("redireccion-status.html")

@app.route('/actualizar-estado-reparacion/<placas>', methods=['GET', 'POST'])
def actualizar_status_reparacion(placas):
    if request.method == 'POST':
        changes = {
        "status.description": request.form["status-d"],
        "status.percentage": request.form["status-p"],
        "client.name": request.form["cliente"],
        "car.model":request.form["carro"],
        "timing.updated": str(datetime.datetime.now())
        }
        orders.find_one_and_update({"car.plates":placas}, {"$set": changes})
        return jsonify({"error": False, "msg": "Status actualizado con exito"})
    orden_servicio = orders.find_one({"car.plates":placas})
    return render_template("status-reparacion-actualizar.html", orden_servicio=orden_servicio)



@app.route('/crear-estado-reparacion', methods=['GET', 'POST'])
def crear_status_reparacion():
    if request.method == 'POST':
        order = {"car": {
        "plates": request.form["placas"],
        "model": request.form["carro"]
        },
        "client" : {
        "name": request.form["cliente"]
        },
        "timing" : {
        "arrival": str(datetime.datetime.now()), #'2021-05-12 01:21:45.456789'
        "updated": str(datetime.datetime.now())
        },
        "work" : {
        "name": request.form["trabajo"]
        },
        "status" : {
        "description": request.form["status-d"],
        "percentage": request.form["status-p"]
        }}
        orders.insert_one(order)
        #lista_usuarios = stringify(db[config["credentials_collection"]].find())
        return jsonify({"error": False, "msg": "Usuario registrado con exito"})
    return render_template("status-reparacion.html")


if __name__ == '__main__':
    #qr = GeneradorQR()
    #qr.mostrar_qr()
    print("Desactive el CORTAFUEGOS si no lo ha hecho")
    app.run(debug=True)
