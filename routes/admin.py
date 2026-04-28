import csv
import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response as FlaskResponse
from flask_login import login_required
from extensions import db
from models import Survey, Question, Option, Response, Answer
from forms import SurveyForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    surveys = Survey.query.order_by(Survey.created_at.desc()).all()
    return render_template('admin/dashboard.html', surveys=surveys)

@admin_bp.route('/survey/create', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')

        survey = Survey(title=title, description=description)
        db.session.add(survey)
        db.session.flush()

        # Собираем вопросы
        question_index = 0
        while True:
            q_text = request.form.get(f'questions-{question_index}-text')
            if q_text is None:
                break

            q_type = request.form.get(f'questions-{question_index}-question_type')
            q_required = request.form.get(f'questions-{question_index}-is_required') == 'y'
            q_sort = request.form.get(f'questions-{question_index}-sort_order', question_index)

            question = Question(
                survey_id=survey.id,
                text=q_text,
                question_type=q_type,
                is_required=q_required,
                sort_order=q_sort
            )
            db.session.add(question)
            db.session.flush()

            # Собираем варианты, если тип radio или checkbox
            if q_type in ('radio', 'checkbox'):
                opt_index = 0
                while True:
                    opt_text = request.form.get(f'questions-{question_index}-options-{opt_index}-text')
                    if opt_text is None:
                        break
                    option = Option(
                        question_id=question.id,
                        text=opt_text,
                        sort_order=opt_index
                    )
                    db.session.add(option)
                    opt_index += 1

            question_index += 1

        db.session.commit()
        flash('Опрос создан!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/survey_form.html', edit=False)

@admin_bp.route('/survey/<int:survey_id>/responses')
@login_required
def view_responses(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    responses = Response.query.filter_by(survey_id=survey_id).order_by(Response.submitted_at.desc()).all()
    return render_template('admin/responses.html', survey=survey, responses=responses)

@admin_bp.route('/survey/<int:survey_id>/responses/csv')
@login_required
def export_csv(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    responses = Response.query.filter_by(survey_id=survey_id).order_by(Response.submitted_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    headers = ['response_id', 'submitted_at', 'ip_address'] + [q.text for q in survey.questions]
    writer.writerow(headers)
    for resp in responses:
        row = [resp.id, resp.submitted_at.strftime('%Y-%m-%d %H:%M:%S'), resp.ip_address]
        for question in survey.questions:
            answer = Answer.query.filter_by(response_id=resp.id, question_id=question.id).first()
            row.append(answer.value if answer else '')
        writer.writerow(row)

    output.seek(0)
    return FlaskResponse(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=survey_{survey_id}_responses.csv'}
    )

@admin_bp.route('/survey/<int:survey_id>/toggle', methods=['POST'])
@login_required
def toggle_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    survey.is_active = not survey.is_active
    db.session.commit()
    status = 'активирован' if survey.is_active else 'деактивирован'
    flash(f'Опрос "{survey.title}" {status}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/survey/<int:survey_id>/delete', methods=['POST'])
@login_required
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    db.session.delete(survey)
    db.session.commit()
    flash(f'Опрос "{survey.title}" удалён.', 'success')
    return redirect(url_for('admin.dashboard'))