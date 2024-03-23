from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField,RadioField
from wtforms.validators import DataRequired,Length,URL
class LoginForm(FlaskForm):
    yxid = StringField("云校账号",validators=[DataRequired(message="云校账号不能为空")])
    password = PasswordField("密码",validators=[DataRequired(message="密码不能为空")])
    submit = SubmitField("提交")
# class WriteForm(FlaskForm):
#     title = StringField("文章标题",validators=[DataRequired(message="文章标题不能为空")])
#     md = TextAreaField("Markdown+HTML文章主体",validators=[DataRequired(message="文章不能为空"),Length(min=10,message="不得小于10个字符")])
#     theme = RadioField("主题色调",choices=[(0,"蓝色（默认）"),(1,"红色"),(2,"橙色"),(3,"绿色")],default=0)
#     jumimg = StringField("文章头图链接",validators=[DataRequired(message="文章头图不能为空"),URL(message="文章头图不是链接")])
#     submit = SubmitField("提交")