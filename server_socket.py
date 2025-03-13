import socket
import sqlite3

## REMPLAZOS PETICION

remplazos = {'%40':'@', '+':' '}

## CONEXION SQLITE3

db = sqlite3.connect('recu_dwes1.db')
cur = db.cursor()

# PRODUCTOS

##cur.execute('INSERT INTO productos (name, price, img) VALUES("Monitor", 100.99, "https://misura.s11.cdn-upgates.com/_cache/1/d/1d0069eb810fe736492c446f78e2c93d-qm24dfi-foto01.jpg")')
##db.commit()

# CREAR TABLA USUARIOS

##CREATE TABLE "usuarios" (
##	"id"	INTEGER,
##	"fullname"	TEXT NOT NULL,
##	"email"	TEXT NOT NULL UNIQUE,
##	"password"	TEXT NOT NULL,
##	PRIMARY KEY("id" AUTOINCREMENT)
##);

## BINDEO HOST Y PORT

HOST = 'localhost'
PORT = 7777

## CARGO HTMLS

# CABECERA

cabecera = 'HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n'

register = open('./templates/register.html', 'r', encoding='UTF-8')
register_html = register.read()
register_f = cabecera
register_f += register_html
register.close()

login = open('./templates/login.html', 'r', encoding='UTF-8')
login_html = login.read()
login_f = cabecera
login_f += login_html
login.close()

tienda = open('./templates/tienda.html', 'r', encoding='UTF-8')
tienda_html = tienda.read()
tienda_f = cabecera
tienda_f += tienda_html
tienda.close()

pasarela = open('./templates/pasarela.html', 'r', encoding='UTF-8')
pasarela_html = pasarela.read()
pasarela_f = cabecera
pasarela_f += pasarela_html
pasarela.close()

carrito = open('./templates/carrito.html', 'r', encoding='UTF-8')
carrito_html = carrito.read()
carrito_f = cabecera
carrito_f += carrito_html
carrito.close()

pedido_final = open('./templates/pedido_final.html', 'r', encoding='UTF-8')
pedido_final_html = pedido_final.read()
pedido_final_f = cabecera
pedido_final_f += pedido_final_html
pedido_final.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as f:

    f.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    f.bind((HOST, PORT))
    f.listen(5)

    while True:

        print('Esperando peticiones...')

        conn, addr = f.accept()
        data = conn.recv(4096)

        respuesta = data.decode('UTF-8').split('\r\n')
        print(respuesta)
        metodo = respuesta[0].split()[0]
        cambio = respuesta[0].split()[1]
        print(metodo, cambio)

        if metodo == 'GET':

            print('SOY UN METODO GET!')

            if cambio == '/':

                print('Soy el register!')
                conn.sendall(register_f.encode('UTF-8'))

            if cambio == '/login.html':

                print('Soy el login!')
                conn.sendall(login_f.encode('UTF-8'))

            if cambio == '/carrito.html':

                print('Soy el carrito!')
                conn.sendall(carrito_f.encode('UTF-8'))

            if cambio == '/tienda.html':

                print('Soy la tienda!')

                productos = cur.execute('SELECT * FROM productos').fetchone() # HAGO UN FETCHONE PORQUE SOLO TENGO UN PRODUCTO PARA HACER PRUEBAS RAPIDAMENTE

                nombre = productos[1]
                precio = productos[2]
                imagen = productos[3]

                conn.sendall(tienda_f.format( 'fullname',imagen, nombre, precio).encode('UTF-8'))

            if cambio == '/pasarela.html':

                print('Soy la pasarela!')
                conn.sendall(pasarela_f.encode('UTF-8'))

            if cambio == '/pedido_final.html':

                print('Soy la confirmacion!')
                conn.sendall(pedido_final_f.encode('UTF-8'))

        if metodo == 'POST':

            print('SOY UN METODO POST!')

            if cambio == '/':

                form = respuesta[-1].split('&')
                fullname = form[0].replace('+', remplazos['+']).split('=')[1]
                email = form[1].replace('%40', remplazos['%40']).split('=')[1]
                password = form[2].replace('+', remplazos['+']).split('=')[1]
                print(fullname, email, password)

                cur.execute('INSERT INTO usuarios (fullname, email, password) VALUES(?, ?, ?)', (fullname, email, password))
                db.commit()

                productos = cur.execute('SELECT * FROM productos').fetchone() # HAGO UN FETCHONE PORQUE SOLO TENGO UN PRODUCTO PARA HACER PRUEBAS RAPIDAMENTE

                nombre = productos[1]
                precio = productos[2]
                imagen = productos[3]

                conn.sendall(tienda_f.format(fullname, imagen, nombre, precio).encode('UTF-8'))

            if cambio == '/login.html':

                form = respuesta[-1].split('&') 
                email = form[0].replace('%40', remplazos['%40']).split('=')[1]
                password = form[1].replace('+', remplazos['+']).split('=')[1]
                print(email, password)

                datos = cur.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()

                if datos:
                    
                    db_id = datos[0]
                    db_fullname = datos[1]
                    db_email = datos[2]
                    db_password = datos[3]

                    print(password, db_password)
                    
                    if password == db_password:

                        print('Sesion iniciada con exito!')

                        productos = cur.execute('SELECT * FROM productos').fetchone() # HAGO UN FETCHONE PORQUE SOLO TENGO UN PRODUCTO PARA HACER PRUEBAS RAPIDAMENTE

                        nombre = productos[1]
                        precio = productos[2]
                        imagen = productos[3]

                        conn.sendall(tienda_f.format(db_fullname, imagen, nombre, precio).encode('UTF-8'))

                    else:

                        print('Error al iniciar sesion!!')
                        conn.sendall(login_f.encode('UTF-8'))
                else:

                    print('Cuenta no encontrado!!')
                    conn.sendall(login_f.encode('UTF-8'))
                    
            if cambio == '/pasarela.html':

                banco = respuesta[-1].split('&')
                tarjeta = form[0].split('=')[1]
                cvv = form[1].split('=')[1]
                fecha_caducidad = form[2].split('=')[1]

                cur.execute('INSERT INTO usuarios (tarjeta, cvv, fecha_caducidad) VALUES(?, ?, ?) WHERE email = ?', (tarjeta, cvv, fecha_caducidad, db_email))
                db.commit()

                conn.sendall(pedido_final_f.encode('UTF-8'))

            if cambio == '/tienda.html':

                cur.execute('INSERT INTO productos (user_id) VALUES (?,)', (db_id,))
                db.commit()

                conn.sendall(tienda_f.format(db_fullname, imagen, nombre, precio).encode('UTF-8'))
