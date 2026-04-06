from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from supabase import create_client
import uuid
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ================= SUPABASE =================
SUPABASE_URL = "https://dlghtzwjtvkrsybztnji.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsZ2h0endqdHZrcnN5Ynp0bmppIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTIxODc4MiwiZXhwIjoyMDkwNzk0NzgyfQ.BB61hZJZIkIWVG0c5LjfF3yrR8LY0_ncTWu-vV04bgc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= DB =================
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres.dlghtzwjtvkrsybztnji:Omar1307jacky@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ================= MODELOS =================
class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    ubicacion = db.Column(db.String(200))
    imagenes = db.relationship("Imagen", backref="proyecto", lazy=True)


class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(500))
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyecto.id"))



# ================= RUTAS PUBLICAS =================


@app.route("/inicio")
def inicio():
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

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/proyectos")
def proyectos():
    proyectos = Proyecto.query.all()
    return render_template("proyectos.html", proyectos=proyectos)


@app.route("/proyecto/<int:id>")
def detalle_proyecto(id):
    proyecto = Proyecto.query.get_or_404(id)
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

        files = request.files.getlist("imagenes")
        print("FILES:", files)

        for file in files:
            if not file or file.filename == "":
                continue

            try:
                # 🔥 extensión real
                ext = file.filename.split(".")[-1].lower()

                # 🔥 nombre único
                file_path = f"{nuevo.id}/{uuid.uuid4()}.{ext}"

                # 🔥 leer archivo
                file_bytes = file.read()

                # 🔥 subir a supabase
                supabase.storage.from_("proyectos").upload(
                    file_path,
                    file_bytes,
                    {"content-type": file.content_type}
                )

                # 🔥 obtener URL (compatible con todas versiones)
                public_url = supabase.storage.from_("proyectos").get_public_url(file_path)

                # 🔥 FIX por si devuelve dict
                if isinstance(public_url, dict):
                    public_url = public_url.get("publicUrl")

                # 🔥 guardar en BD
                if public_url:
                    img = Imagen(filename=public_url, proyecto_id=nuevo.id)
                    db.session.add(img)
                else:
                    print("ERROR: No se obtuvo URL")

            except Exception as e:
                print("ERROR SUBIENDO:", e)

        db.session.commit()
        return redirect("/admin")

    proyectos = Proyecto.query.all()
    return render_template("admin.html", proyectos=proyectos)

# ================= EDITAR =================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_proyecto(id):
    if not session.get("admin"):
        return redirect("/login")

    proyecto = Proyecto.query.get_or_404(id)

    if request.method == "POST":
        proyecto.nombre = request.form["nombre"]
        proyecto.ubicacion = request.form["ubicacion"]

        files = request.files.getlist("imagenes")

        for file in files:
            if not file or file.filename == "":
                continue

            try:
                # 🔥 extensión real
                ext = file.filename.split(".")[-1].lower()

                # 🔥 nombre único
                file_path = f"{id}/{uuid.uuid4()}.{ext}"

                # 🔥 leer archivo
                file_bytes = file.read()

                # 🔥 subir a supabase
                supabase.storage.from_("proyectos").upload(
                    file_path,
                    file_bytes,
                    {"content-type": file.content_type}
                )

                # 🔥 obtener URL correctamente
                public_url = supabase.storage.from_("proyectos").get_public_url(file_path)

                # 🔥 compatibilidad
                if isinstance(public_url, dict):
                    public_url = public_url.get("publicUrl")

                # 🔥 guardar en BD
                if public_url:
                    img = Imagen(filename=public_url, proyecto_id=id)
                    db.session.add(img)
                else:
                    print("ERROR: No se obtuvo URL")

            except Exception as e:
                print("ERROR SUBIENDO:", e)

        db.session.commit()
        return redirect("/admin")

    return render_template("editar.html", proyecto=proyecto)

# ================= ELIMINAR PROYECTO =================
@app.route("/eliminar/<int:id>")
def eliminar_proyecto(id):
    if not session.get("admin"):
        return redirect("/login")

    proyecto = Proyecto.query.get_or_404(id)

    imagenes = Imagen.query.filter_by(proyecto_id=id).all()

    paths = []

    for img in imagenes:
        try:
            if img.filename and "proyectos/" in img.filename:
                # 🔥 forma segura
                path = img.filename.split("proyectos/")[1]
                paths.append(path)
        except Exception as e:
            print("ERROR PROCESANDO PATH:", e)

    # 🔥 eliminar en lote (mejor)
    if paths:
        try:
            supabase.storage.from_("proyectos").remove(paths)
        except Exception as e:
            print("ERROR ELIMINANDO STORAGE:", e)

    # 🔥 eliminar de BD
    Imagen.query.filter_by(proyecto_id=id).delete()

    db.session.delete(proyecto)
    db.session.commit()

    return redirect("/admin")

# ================= ELIMINAR IMAGEN =================
@app.route("/eliminar-imagen/<int:id>")
def eliminar_imagen(id):
    if not session.get("admin"):
        return redirect("/login")

    img = Imagen.query.get_or_404(id)
    proyecto_id = img.proyecto_id

    try:
        if img.filename and "proyectos/" in img.filename:
            # 🔥 obtener path de forma segura
            path = img.filename.split("proyectos/")[1]

            supabase.storage.from_("proyectos").remove([path])

    except Exception as e:
        print("ERROR ELIMINANDO STORAGE:", e)

    # 🔥 eliminar de BD SIEMPRE
    db.session.delete(img)
    db.session.commit()

    return redirect(f"/editar/{proyecto_id}")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)