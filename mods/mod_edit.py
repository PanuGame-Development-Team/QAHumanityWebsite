import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from flask import *
from model import *
from settings import *
from lib import *
app = Blueprint(name="edit",url_prefix="/edit",import_name="edit")
@app.route("/",methods=["GET"])
def index():
    return redirect(url_for("edit.conf"))
@app.route("/conf",methods=["GET","POST"])
def conf():
    if session.get("logged_in"):
        dic = {"user":session.get("user"),"uid":session.get("uid"),"version":APP_VERSION}
    else:
        return redirect("/login/")
    if request.method == "GET":
        return render_template("mod_conf/conf.html",**dic)
    elif lin(["nickname","password1","password2"],request.form) and lin(["headimg"],request.files):
        user = getuser_id(dic["uid"])
        nickname = request.form["nickname"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if not check_password_hash(user.passwd,password1):
            flash("原密码不匹配","danger")
            return redirect(url_for("edit.conf"))
        headimg = request.files.getlist("headimg")[0]
        user.nickname = nickname
        if headimg.filename:
            user.headimg = save_file(headimg,["jpg","png","jpeg","gif"])
        else:
            user.headimg = "/static/user.jpg"
        user.passwd = generate_password_hash(password2)
        db.session.commit()
        flash("修改成功","success")
        return redirect("/")
    else:
        abort(404)