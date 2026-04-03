from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# 🔐 SECRET KEY
app.secret_key = "supersecretkey"

# 🟢 SUPABASE (PON TU CONEXIÓN AQUÍ)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres.dlghtzwjtvkrsybztnji:Omar1307jacky@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 📁 CARPETA DE IMÁGENES
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

# ================= MODELOS =================


class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    ubicacion = db.Column(db.String(200))

    imagenes = db.relationship("Imagen", backref="proyecto", lazy=True)


class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyecto.id"))


# ================= RUTAS =================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_proyecto(id):
    if not session.get("admin"):
        return redirect("/login")

    proyecto = Proyecto.query.get(id)

    if request.method == "POST":
        proyecto.nombre = request.form["nombre"]
        proyecto.ubicacion = request.form["ubicacion"]

        db.session.commit()

        # 📸 NUEVAS IMÁGENES
        files = request.files.getlist("imagenes")

        carpeta = os.path.join(app.config["UPLOAD_FOLDER"], str(id))
        os.makedirs(carpeta, exist_ok=True)

        for i, file in enumerate(files):

            if file.filename == "":
                continue

            if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue

            filename = f"{len(proyecto.imagenes)+i+1}.jpg"
            ruta = os.path.join(carpeta, filename)
            file.save(ruta)

            img = Imagen(filename=f"{id}/{filename}", proyecto_id=id)
            db.session.add(img)

        db.session.commit()

        return redirect("/admin")

    # 👇 ESTE SIEMPRE VA AL FINAL
    return render_template("editar.html", proyecto=proyecto)

@app.route("/eliminar/<int:id>")
def eliminar_proyecto(id):
    if not session.get("admin"):
        return redirect("/login")

    proyecto = Proyecto.query.get(id)

    # borrar imágenes BD
    Imagen.query.filter_by(proyecto_id=id).delete()

    db.session.delete(proyecto)
    db.session.commit()

    return redirect("/admin")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/servicios")
def servicios():
    return render_template("servicios.html")


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


@app.route("/aviso")
def aviso():
    return render_template("aviso.html")


# 🔥 PROYECTOS DINÁMICOS
@app.route("/proyectos")
def proyectos():
    proyectos = Proyecto.query.all()
    return render_template("proyectos.html", proyectos=proyectos)


# 🔥 DETALLE DE PROYECTO
@app.route("/proyecto/<int:id>")
def detalle_proyecto(id):
    proyecto = Proyecto.query.get(id)
    imagenes = Imagen.query.filter_by(proyecto_id=id).all()
    return render_template("detalle.html", proyecto=proyecto, imagenes=imagenes)


# ================= LOGIN =================


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["user"] == "Admin" and request.form["pass"] == "mexico24":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# ================= ADMIN =================


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        nombre = request.form["nombre"]
        ubicacion = request.form["ubicacion"]

        nuevo = Proyecto(nombre=nombre, ubicacion=ubicacion)
        db.session.add(nuevo)
        db.session.commit()

        carpeta = os.path.join(app.config["UPLOAD_FOLDER"], str(nuevo.id))
        os.makedirs(carpeta, exist_ok=True)

        files = request.files.getlist("imagenes")

        for i, file in enumerate(files):
            filename = f"{i+1}.jpg"
            ruta = os.path.join(carpeta, filename)
            file.save(ruta)

            img = Imagen(filename=f"{nuevo.id}/{filename}", proyecto_id=nuevo.id)
            db.session.add(img)

        db.session.commit()

        return redirect("/proyectos")

    # 🔥 ESTO FALTABA
    proyectos = Proyecto.query.all()
    return render_template("admin.html", proyectos=proyectos)


@app.route("/eliminar-imagen/<int:id>")
def eliminar_imagen(id):
    if not session.get("admin"):
        return redirect("/login")

    img = Imagen.query.get(id)

    ruta = os.path.join("static/uploads", img.filename)

    if os.path.exists(ruta):
        os.remove(ruta)

    proyecto_id = img.proyecto_id

    db.session.delete(img)
    db.session.commit()

    return redirect(f"/editar/{proyecto_id}")


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
