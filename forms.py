from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class OptionForm(FlaskForm):
    text = StringField('Вариант', validators=[DataRequired()])
    sort_order = HiddenField('0')

class QuestionForm(FlaskForm):
    text = StringField('Текст вопроса', validators=[DataRequired()])
    question_type = SelectField('Тип', choices=[
        ('radio', 'Одиночный выбор'),
        ('checkbox', 'Множественный выбор'),
        ('text', 'Текст'),
        ('textarea', 'Многострочный текст'),
        ('rating', 'Оценка (1-5)')
    ])
    is_required = BooleanField('Обязательный')
    sort_order = HiddenField('0')
    options = FieldList(FormField(OptionForm), min_entries=1)

class SurveyForm(FlaskForm):
    title = StringField('Название опроса', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание')
    questions = FieldList(FormField(QuestionForm), min_entries=1)
    submit = SubmitField('Сохранить')