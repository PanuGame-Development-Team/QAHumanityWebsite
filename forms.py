from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField,RadioField,IntegerField,BooleanField
from wtforms.validators import DataRequired,Length,URL
class LoginForm(FlaskForm):
    yxid = StringField("云校账号",validators=[DataRequired(message="云校账号不能为空")])
    password = PasswordField("密码",validators=[DataRequired(message="密码不能为空")])
    submit = SubmitField("提交")
class Admin_User(FlaskForm):
    realname = StringField("真实姓名",validators=[DataRequired(message="真实姓名不能为空")])
    passwd = PasswordField("强制修改密码",validators=[])
    nickname = StringField("外号标签",validators=[])
    submit = SubmitField("提交")
class Admin_Article(FlaskForm):
    title = StringField("标题",validators=[DataRequired(message="标题不能为空")])
    html = TextAreaField("HTML文本",validators=[DataRequired(message="正文不能为空")])
    submit = SubmitField("提交")
class Admin_Comment(FlaskForm):
    comment = StringField("评论",validators=[DataRequired(message="评论不能为空")])
    submit = SubmitField("提交")