from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Survey, Response, Answer
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    surveys = Survey.query.filter_by(is_active=True).order_by(Survey.created_at.desc()).all()
    return render_template('index.html', surveys=surveys)

@public_bp.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
def take_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if not survey.is_active:
        flash('Опрос неактивен или завершён.', 'warning')
        return render_template('survey_closed.html')

    if request.method == 'POST':
        # Проверка дублирования с того же IP
        existing = Response.query.filter_by(
            survey_id=survey_id,
            ip_address=request.remote_addr
        ).first()
        if existing:
            flash('Вы уже проходили этот опрос.', 'warning')
            return redirect(url_for('public.thanks'))

        response = Response(
            survey_id=survey_id,
            submitted_at=datetime.utcnow(),
            ip_address=request.remote_addr
        )
        db.session.add(response)
        db.session.flush()

        for question in survey.questions:
            if question.question_type in ('radio', 'rating'):
                value = request.form.get(f'q_{question.id}')
            elif question.question_type == 'checkbox':
                selected = request.form.getlist(f'q_{question.id}')
                value = ','.join(selected) if selected else ''
            else:
                value = request.form.get(f'q_{question.id}', '')

            if question.is_required and not value:
                db.session.rollback()
                flash(f'Поле «{question.text}» обязательно для заполнения.', 'danger')
                return render_template('survey.html', survey=survey, questions=survey.questions)

            answer = Answer(
                response_id=response.id,
                question_id=question.id,
                value=value
            )
            db.session.add(answer)

        db.session.commit()
        return redirect(url_for('public.thanks'))

    return render_template('survey.html', survey=survey, questions=survey.questions)

@public_bp.route('/thanks')
def thanks():
    return render_template('thanks.html')