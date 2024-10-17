from flask import Flask, render_template, jsonify, request, redirect, url_for, Response
import sqlite3
import xml.etree.ElementTree as ET
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, set_access_cookies, verify_jwt_in_request
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'yametekudasai'  # Cambia esto a un valor seguro
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1", "http://localhost:5000", "http://127.0.0.1:5000"])
jwt = JWTManager(app)

app.secret_key = 'yametekudasai'  
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

app.app_context()

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    pages = []
    # Páginas estáticas
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
    static_pages = [
        ['/', ten_days_ago],
        ['/sobre-nosotros', ten_days_ago],
        ['/contacto', ten_days_ago],
        ['/terminos-y-condiciones', ten_days_ago],
    ]
    for page in static_pages:
        pages.append([page[0], page[1]])

    # Páginas dinámicas (artículos)
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id_articulo, titulo, fecha_ultima_edicion FROM articulos")
    articles = cursor.fetchall()
    conn.close()

    for article in articles:
        article_id = article[0]
        slug = article[1].replace(' ', '-').lower()
        last_mod = article[2] if article[2] else ten_days_ago
        pages.append([f'/articulo/{article_id}/{slug}', last_mod])

    # Construcción del XML del sitemap
    sitemap_xml = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for page in pages:
        url = ET.SubElement(sitemap_xml, 'url')
        loc = ET.SubElement(url, 'loc')
        loc.text = f'http://yourdomain.com{page[0]}'
        lastmod = ET.SubElement(url, 'lastmod')
        lastmod.text = page[1]
        changefreq = ET.SubElement(url, 'changefreq')
        changefreq.text = 'monthly'  # Puedes ajustarlo según tus necesidades
        priority = ET.SubElement(url, 'priority')
        priority.text = '0.8'  # Las páginas más importantes pueden tener prioridad más alta

    xml_string = ET.tostring(sitemap_xml, encoding='utf-8', method='xml')
    
    response = Response(xml_string, mimetype='application/xml')
    return response

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    # Buscar el usuario por su ID en la base de datos
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id_autor, alias, password FROM autores WHERE id_autor = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        user = User(id=user_data[0], username=user_data[1], password=user_data[2])
        return user
    return None

@app.route('/')
def home():
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()

    # Obtener los artículos recientes
    cursor.execute("""
        SELECT a.id_articulo, a.titulo, a.fecha_creacion, a.fecha_ultima_edicion, a.url_imagen, a.figma_imagen,
               GROUP_CONCAT(t.nombre, ', ') AS tags
        FROM articulos a
        LEFT JOIN articulo_tags at ON a.id_articulo = at.id_articulo
        LEFT JOIN tags t ON at.id_tag = t.id_tag
        GROUP BY a.id_articulo
        ORDER BY a.fecha_creacion DESC
        LIMIT 10;
    """)
    resultados_articulos = cursor.fetchall()

    # Obtener los artículos destacados
    cursor.execute("""
        SELECT a.id_articulo, a.titulo, a.fecha_creacion, a.fecha_ultima_edicion, a.url_imagen, a.figma_imagen,
               GROUP_CONCAT(t.nombre, ', ') AS tags
        FROM articulos a
        LEFT JOIN articulo_tags at ON a.id_articulo = at.id_articulo
        LEFT JOIN tags t ON at.id_tag = t.id_tag
        INNER JOIN destacados d ON a.id_articulo = d.id_articulo
        WHERE d.destacado = 1
        GROUP BY a.id_articulo
        ORDER BY a.id_articulo DESC
        LIMIT 3;
    """)
    resultados_destacados = cursor.fetchall()

    # Define las columnas
    columnas = ["ID_Articulo", "Titulo", "Fecha_Creacion", "Fecha_Ultima_Edicion", "Url_Image", "Figma", "Tags"]

    # Procesar artículos recientes
    articulos_recientes = [
        {**dict(zip(columnas, articulo)), 'Tags': articulo[-1].split(', ') if articulo[-1] else []}
        for articulo in resultados_articulos
    ]

    # Procesar artículos destacados
    articulos_destacados = [
        {**dict(zip(columnas, articulo)), 'Tags': articulo[-1].split(', ') if articulo[-1] else []}
        for articulo in resultados_destacados
    ]

    conn.close()
    return render_template('index.html', articulos_recientes=articulos_recientes, articulos_destacados=articulos_destacados)

@app.route('/sobre-nosotros')
def about_us():
    return render_template('aboutus.html')

@app.route('/contacto')
def contact():
    return render_template('contacto.html')

@app.route('/api/enviar-contacto', methods=["POST"]) #Conectar a algo
def contact_api():
    nombre = request.form['nombre']
    email = request.form['email']
    mensaje = request.form['mensaje']
    print(nombre, email, mensaje)
    return jsonify(message='Mensaje enviado con éxito'), 200

@app.route('/terminos-y-condiciones')
def terminos_y_condiciones():
    return render_template('terms.html')

@app.route('/api/register', methods=['POST'])
def register():
    id = 1
    alias = 'admin123'
    nombre = 'admin escritor'
    password = '1234'
    gmail = 'adminescritor@gmail.com'
    hashed_password = generate_password_hash(password)
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO autores (id_autor, alias, nombre_completo, password, email) VALUES (?,?,?,?,?)', (id, alias, nombre, hashed_password, gmail))
    conn.commit()
    conn.close()

    return jsonify(message='User registered successfully'), 201

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        conn = sqlite3.connect('./peliculas.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM autores WHERE alias = ?', (username,))
        userpass = cursor.fetchone()
        print(userpass)
        conn.close()
        if userpass and check_password_hash(userpass[0], password):
            print('user correcto')
            access_token = create_access_token(identity=username)
            token = jsonify({'token':access_token})
            set_access_cookies(token, access_token)
            print(access_token)
            return token
        else:
            return jsonify({'message': 'Credenciales incorrectas'}), 401

@app.route("/busqueda")
def search():
    query = request.args.get('query', '')
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id_articulo, a.titulo, a.fecha_creacion, a.fecha_ultima_edicion, a.url_imagen,
               GROUP_CONCAT(t.nombre, ', ') AS tags
        FROM articulos a
        LEFT JOIN articulo_tags at ON a.id_articulo = at.id_articulo
        LEFT JOIN tags t ON at.id_tag = t.id_tag
        WHERE a.titulo LIKE ?
        GROUP BY a.id_articulo
    ''', ('%' + query + '%',))
    
    resultados = cursor.fetchall()
    conn.close()
    
    # Definir las columnas
    columnas = ["ID", "Titulo", "Fecha_Creacion", "Fecha_Ultima_Edicion", "Url_Imagen", "Tags"]

    # Procesar resultados y manejar los tags como lista
    articulos = [
        {**dict(zip(columnas, articulo)), 'Tags': articulo[-1].split(', ') if articulo[-1] else []}
        for articulo in resultados
    ]

    return render_template('busqueda.html', articulos=articulos, query=query)

@app.route('/articulo/<int:art_id>/<string:slug>') # Añadir tags
def articulo(art_id,slug):
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id_articulo, a.titulo, a.contenido_html, a.fecha_creacion, 
               a.fecha_ultima_edicion, au.nombre_completo, a.url_imagen, 
               GROUP_CONCAT(t.nombre, ', ') AS tags
        FROM articulos a
        JOIN autores au ON a.id_autor = au.id_autor
        LEFT JOIN articulo_tags at ON a.id_articulo = at.id_articulo
        LEFT JOIN tags t ON at.id_tag = t.id_tag
        WHERE a.id_articulo = ?
        GROUP BY a.id_articulo
    ''', (art_id,))
    articulo_data = cursor.fetchone()
    
    if articulo_data:
        columns = ["ID","Titulo", "Contenido_HTML", "Fecha_Creacion", "Fecha_Ultima_Edicion", "Autor", "Url_Imagen", "Tags"]
        articulo = dict(zip(columns, articulo_data))
        expected_slug = articulo['Titulo'].replace(' ', "-").lower()
        if expected_slug != slug:
            return redirect(url_for('articulo', art_id=art_id, slug=expected_slug), 301)
        
        current_tags = articulo['Tags'].split(', ') 
        
        # Obtener artículos relacionados por tags
        if current_tags:
            placeholders = ','.join('?' for _ in current_tags)
            query = f'''
                SELECT a.id_articulo, a.titulo, a.url_imagen
                FROM articulos a
                JOIN articulo_tags at ON a.id_articulo = at.id_articulo
                JOIN tags t ON at.id_tag = t.id_tag
                WHERE a.id_articulo != ?
                AND t.nombre IN ({placeholders})
                GROUP BY a.id_articulo
                LIMIT 3
            '''
            cursor.execute(query, (art_id, *current_tags))
            related_articulos = cursor.fetchall()
        else:
            related_articulos = []
        
        conn.close()
        
        related_columns = ['ID', 'Titulo', 'Nombre_Imagen', 'Url_Imagen']
        relacionados = [dict(zip(related_columns, articulo)) for articulo in related_articulos]
        return render_template('articulo.html', articulo=articulo, relacionados=relacionados)
    
    else:
        return jsonify(message='Articulo no encontrado'), 404

@app.route("/api/crear-articulo", methods=["GET", "POST"])
def crear_articulo():
    if request.method == "GET":
        return render_template('creador.html')
    
    if request.method == "POST":
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            print(f"Usuario autenticado: {current_user}")
        except Exception as e:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        titulo = request.form['title']
        AUTOR = 1  # Reemplazar en el futuro por current_user
        contenido_html = request.form['content_html']
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        url_imagen = request.form.get('url_image', "https://i.pinimg.com/564x/f2/81/0c/f2810c5ba7196821948d93ba338d2190.jpg")
        figma_imagen = request.form.get('figma_image', "")

        tags_strings = request.form['tags']
        destacado = int(request.form.get('destacado', 0))

        tag_list = [tag.strip() for tag in tags_strings.split(',') if tag.strip()]  # Eliminar espacios y tags vacíos

        conn = sqlite3.connect('./peliculas.db')
        cursor = conn.cursor()

        # Insertar el nuevo artículo
        cursor.execute('''
            INSERT INTO articulos (titulo, contenido_html, fecha_creacion, id_autor, url_imagen, figma_imagen) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (titulo, contenido_html, fecha_creacion, AUTOR, url_imagen, figma_imagen))
        
        # Obtener el id del nuevo artículo
        articulo_id = cursor.lastrowid

        # Gestionar los tags: insertar los tags si no existen, y crear la relación en `articulo_tags`
        for tag in tag_list:
            cursor.execute('SELECT id_tag FROM tags WHERE nombre = ?', (tag,))
            tag_data = cursor.fetchone()
            if tag_data:
                tag_id = tag_data[0]
            else:
                cursor.execute('INSERT INTO tags (nombre) VALUES (?)', (tag,))
                tag_id = cursor.lastrowid

            # Insertar en la tabla intermedia `articulo_tags`
            cursor.execute('INSERT INTO articulo_tags (id_articulo, id_tag) VALUES (?, ?)', (articulo_id, tag_id))

        # Insertar el artículo en la tabla `destacados` si está marcado como destacado
        cursor.execute('''
            INSERT INTO destacados (id_articulo, destacado) 
            VALUES (?, ?)
        ''', (articulo_id, destacado))
        
        conn.commit()
        conn.close()

        # Retornar una respuesta válida con código 200 (OK)
        return jsonify(message='Artículo creado con éxito'), 200

@app.route('/api/destacar-articulo/<int:artID>', methods=['POST'])
def destacar_articulo(artID):
        print('methodo recibido')
        destacar = request.json['destacar']
        try:
                token = request.cookies.get('token')
                print(token)
                verify_jwt_in_request()  # Verificar si el token JWT está presente
                current_user = get_jwt_identity()  # Obtener la identidad del usuario desde el JWT
                print(f"Usuario autenticado con extended: {current_user}")
                if destacar:
                    print(destacar)
                    print(destacar == False)
                    conn = sqlite3.connect('./peliculas')
                    cursor = conn.cursor()
                    cursor.execute('''
                                    INSERT INTO destacados (id_articulo, destacado)
                                    VALUES (?, ?)
                                    ON CONFLICT(id_articulo) DO UPDATE SET destacado = excluded.destacado;
                                   ''',(artID, 1 if destacar else 0))
                    conn.commit()
                    conn.close()
                    return jsonify({'message':'Articulo destacado con exito'})
                elif destacar == False:
                    conn = sqlite3.connect('./peliculas')
                    cursor = conn.cursor()
                    cursor.execute('''
                                    INSERT INTO destacados (id_articulo, destacado)
                                    VALUES (?, ?)
                                    ON CONFLICT(id_articulo) DO UPDATE SET destacado = excluded.destacado;
                                   ''',(artID, 0 if destacar else 1))
                    conn.commit()
                    conn.close()
                    return jsonify({'message':'Articulo Des-destacado con exito'})
        except Exception as e:
            print(e)
            print({'message': 'Token inválido o expirado'}), 401
            return jsonify({"message":'Ha ocurrido algo durante la destacacion'})
        
        
@app.route('/perfil/<int:perfil_id>', methods=["GET", "POST"]) # Añadir tags para los articulos
def perfil(perfil_id):
    current_user='guest'
    
    if request.method == "POST":
            try:
                token = request.cookies.get('token')
                print(token)
                verify_jwt_in_request()  # Verificar si el token JWT está presente
                current_user = get_jwt_identity()  # Obtener la identidad del usuario desde el JWT
                print(f"Usuario autenticado con extended: {current_user}")
                return jsonify({'message':'Auth success', 'Auth':True}), 200
            except Exception as e:
                print(e)
                print({'message': 'Token inválido o expirado'}), 401
    
    try:
            token = request.cookies.get('token')
            print(token)
            verify_jwt_in_request()  # Verificar si el token JWT está presente
            current_user = get_jwt_identity()  # Obtener la identidad del usuario desde el JWT
            print(f"Usuario autenticado con extended: {current_user}")
    except Exception as e:
            print(e)
            print({'message': 'Token inválido o expirado'}), 401
    
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT au.id_autor, au.nombre_completo, au.email, au.alias, a.id_articulo, 
               a.titulo, a.contenido_html, a.fecha_creacion, 
               a.fecha_ultima_edicion, a.url_imagen, a.likes
        FROM autores au
        LEFT JOIN articulos a ON a.id_autor = au.id_autor
        WHERE au.id_autor = ?
    ''', (perfil_id,))
    data = cursor.fetchall()
    conn.close()
    if data:
        autor_columns = ["ID_Escritor", "Nombre_Completo", "Email", 'Alias']
        articulo_columns = ["ID_Articulo", "Titulo", "Contenido_HTML", "Fecha_Creacion", "Fecha_Ultima_Edicion", "URL_Imagen"]
        
        autor = dict(zip(autor_columns, data[0][:4]))
        articulos = [dict(zip(articulo_columns, row[4:])) for row in data]
    
        return render_template('miperfil.html', autor=autor, articulos=articulos, current_user=current_user)
    else:
        return jsonify(message='Perfil no encontrado'), 404
    
@app.route('/api/editar-articulo/<int:art_id>', methods=["GET", "POST"]) # Fecha, date time
def editar_articulo(art_id):
    if request.method == "GET":
        conn = sqlite3.connect('./peliculas.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articulos WHERE id_articulo = ?', (art_id,))
        articulo_data = cursor.fetchone()
        conn.close()
        
        if articulo_data:
            columns = ["ID", "Titulo", "Contenido_HTML", "Fecha_Creacion", "Fecha_Ultima_Edicion", "Autor", "Url_Imagen", "Figma_Image"]
            articulo = dict(zip(columns, articulo_data)) 
            
            # Obtener tags del artículo
            conn = sqlite3.connect('./peliculas.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.nombre 
                FROM tags t
                JOIN articulo_tags at ON t.id_tag = at.id_tag
                WHERE at.id_articulo = ?
            ''', (art_id,))
            tags = cursor.fetchall()
            articulo['Tags'] = ', '.join([tag[0] for tag in tags])  # Convertir lista de tags a cadena separada por comas
            conn.close()
            return render_template('editor.html', articulo=articulo)
        else:
            return jsonify(message='Artículo no encontrado'), 404
        
    elif request.method == "POST":
        try:
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            print(f"Usuario autenticado: {current_user}")
        except Exception as e:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        titulo = request.form['title']
        articulo_id = art_id
        contenido_html = request.form['content_html']
        url_imagen = request.form['url_image']
        figma_imagen = request.form['figma_image']
        fecha_ultima_edicion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Obtener los tags
        tags_strings = request.form['tags']
        tag_list = [tag.strip() for tag in tags_strings.split(',') if tag.strip()]  # Eliminar espacios y tags vacíos

        conn = sqlite3.connect('./peliculas.db')
        cursor = conn.cursor()

        # Actualizar el artículo
        cursor.execute('''
            UPDATE articulos 
            SET titulo = ?, contenido_html = ?, fecha_ultima_edicion = ?, url_imagen = ?, figma_imagen = ?
            WHERE id_articulo = ?
        ''', (titulo, contenido_html, fecha_ultima_edicion, url_imagen, figma_imagen, articulo_id))

        # Eliminar los tags existentes
        cursor.execute('DELETE FROM articulo_tags WHERE id_articulo = ?', (articulo_id,))

        # Insertar nuevos tags y relaciones
        for tag in tag_list:
            cursor.execute('SELECT id_tag FROM tags WHERE nombre = ?', (tag,))
            tag_data = cursor.fetchone()
            if tag_data:
                tag_id = tag_data[0]
            else:
                cursor.execute('INSERT INTO tags (nombre) VALUES (?)', (tag,))
                tag_id = cursor.lastrowid

            # Insertar la relación entre artículo y tag (siempre)
            cursor.execute('INSERT INTO articulo_tags (id_articulo, id_tag) VALUES (?, ?)', (articulo_id, tag_id))

        conn.commit()
        conn.close()

        return jsonify(message='Artículo modificado con éxito'), 200
  
@app.route('/api/eliminar-articulo/<int:art_id>', methods=['DELETE'])
def eliminar_articulo(art_id):
    
    try:
        verify_jwt_in_request()  # Verificar si el token JWT está presente
        current_user = get_jwt_identity()  # Obtener la identidad del usuario desde el JWT
        print(f"Usuario autenticado con extended: {current_user}")
    except Exception as e:
        return jsonify({'message': 'Token inválido o expirado'}), 401
    
    conn = sqlite3.connect('./peliculas.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM articulo_tags WHERE id_articulo = ?', (art_id,))
        cursor.execute('DELETE FROM articulos WHERE id_articulo = ?', (art_id,))
        cursor.execute('''
    DELETE FROM tags
    WHERE id_tag NOT IN (SELECT DISTINCT id_tag FROM articulo_tags)
''')
        conn.commit()
        return jsonify(message='Artículo eliminado con éxito'), 200
    except Exception as e:
        return jsonify(message='Error al eliminar el artículo: ' + str(e)), 400
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)