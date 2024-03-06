from flask import Flask,request,redirect,render_template,abort
from settings import *
from lib import *
from model import *
app = Flask(APP_NAME)
app.secret_key = APP_SECRETKEY
for config in APP_CONFIG:
    app.config[config] = APP_CONFIG[config]
db.init_app(app)
@app.template_filter("tag_format")
def tagf(html:str,themeid):
    if themeid == 0:
        theme = "primary"
    elif themeid == 1:
        theme = "danger"
    elif themeid == 2:
        theme = "warning"
    elif themeid == 3:
        theme = "success"
    return html.format(theme=theme)
@app.template_filter("del_tag")
def deltag(html:str):
    return html.translate({ord(i):None for i in "abcdefghijklmnopqrstuvwxyz1234567890 !-\"'<>/%\{\}=#."})
@app.route("/",methods=["GET"])
def index():
    try:
        id = int(request.args.get("id",-1))
        article = Article.query.get(id)
        newest = Article.query.order_by(Article.id.desc()).limit(10).all()
        if article:
            return render_template("page.html",article=article,newest=newest)
        abort(404)
    except Exception as e:
        return str(e)
if __name__ == "__main__":
    app.run(HOST,PORT,DEBUG)