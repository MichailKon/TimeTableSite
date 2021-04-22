import datetime
import os

from flask import Flask, render_template, redirect, request, abort, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from flask_restful import Api, abort

from constants import MAX_SUBJECTS
from data import db_session
from data.days import Day
from data.homework import Homework
from data.schedules import Schedule
from data.subjects import Subject
from data.users import User
from forms import user_forms, schedule_forms, homework_forms

from api.v1 import schedule_api, subjects_api, homework_api

from constants import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
import uuid

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
app.config['SECRET_KEY'] = '267iokdonibf890wi4k23ioruh8fuipokaldfsa'
app.config['UPLOAD_FOLDER'] = 'dynamic'


def get_start_and_end_date_from_calendar_week(year, calendar_week):
    monday = datetime.datetime.strptime(f'1.{calendar_week}.{year}', "%w.%W.%Y").date()
    return monday.strftime("%d.%m.%Y"), (monday + datetime.timedelta(days=6.9)).strftime("%d.%m.%Y")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def start_page():
    return redirect("/schedule")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = user_forms.LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/schedule")
        return render_template('login.html', message='Wrong login or password', form=form)
    return render_template('login.html', title='Sign in', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = user_forms.RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Sign up',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Sign in',
                                   form=form, message='Человек с таким логином уже существует')
        user = User(surname=form.surname.data, name=form.name.data,
                    age=form.age.data, email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Sign up', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/schedule')


def get_schedule(day=None, subj_num=None):
    db_sess = db_session.create_session()
    query = db_sess.query(Schedule, Day, Subject)
    query = query.join(Day, Day.day_id == Schedule.schedule_day)
    query = query.join(Subject, Subject.subject_id == Schedule.schedule_subject)
    if day is not None:
        query = query.filter(Schedule.schedule_day == day)
    if subj_num is not None:
        query = query.filter(Schedule.schedule_num == subj_num)

    return query.all()


def get_subjects():
    db_sess = db_session.create_session()
    query = db_sess.query(Subject).order_by(Subject.subject_name)
    return [i.subject_name for i in query.all()]


@app.route('/schedule')
def show_schedule():
    schedule = {}

    for i in get_schedule():
        now = schedule.get(i.Day.day_id, {})
        schedule[i.Day.day_id] = now
        now[i.Schedule.schedule_num] = i.Subject.subject_name
        schedule[i.Day.day_id] = now

    db_sess = db_session.create_session()
    days = db_sess.query(Day).all()
    return render_template('schedule.html', title='Schedule',
                           schedule=schedule, days=days, max_subjects=MAX_SUBJECTS)


@app.route('/schedule/<int:day_num>', methods=['GET', 'POST'])
@login_required
def edit_subjects(day_num):
    form = schedule_forms.EditSubjects()
    db_sess = db_session.create_session()
    day_name = db_sess.query(Day).filter(Day.day_id == day_num).first()
    if not day_name:
        abort(404)
    day_name = day_name.day_name
    subj = get_subjects()

    for subj_num in range(1, MAX_SUBJECTS + 1):
        exec(f'form.subject_{subj_num}.choices = {subj}')

    if request.method == "GET":
        query = db_sess.query(Schedule, Subject)
        query = query.join(Subject, Subject.subject_id == Schedule.schedule_subject)
        query = query.filter(Schedule.schedule_day == day_num)
        schedule = query.all()
        for i in schedule:
            exec(f'form.subject_{i.Schedule.schedule_num}.default = "{i.Subject.subject_name}"')
        form.process()
        return render_template('subject_edit.html', title='Edit schedule',
                               day_name=day_name, form=form, subjects=subj)
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect('/schedule')
        for subj_num in range(1, MAX_SUBJECTS + 1):
            subj = db_sess.query(Schedule).filter(Schedule.schedule_day == day_num,
                                                  Schedule.schedule_num == subj_num)
            subj = subj.first()

            form_subj = eval(f'form.subject_{subj_num}.data')

            if subj and form_subj:
                subj.schedule_subject = db_sess.query(Subject). \
                    filter(Subject.subject_name == form_subj).first().subject_id
            elif subj and not form_subj:
                db_sess.delete(subj)
            elif subj is None and form_subj:
                new_subject = db_sess.query(Subject).filter(Subject.subject_name == form_subj).first()
                new_subject: Subject
                subject = Schedule(schedule_subject=new_subject.subject_id,
                                   schedule_day=day_num,
                                   schedule_num=subj_num)
                db_sess.add(subject)
        db_sess.commit()
        return redirect('/schedule')
    return render_template('subject_edit.html', title='Edit schedule',
                           day_name=day_name, form=form, subjects=subj)


@app.route('/homework')
def redirect_from_pure_homework():
    year, week_num, day_of_week = datetime.date.today().isocalendar()
    return redirect(f'/homework/{year}/{week_num}')


@app.route('/homework/<int:year>/<int:week>')
def show_homework(year, week):
    db_sess = db_session.create_session()
    homework = {}
    # pick schedule
    for i in get_schedule():
        now = homework.get(i.Day.day_id, {})
        now[i.Schedule.schedule_num] = now.get(i.Schedule.schedule_num, {})
        now[i.Schedule.schedule_num]['subject_title'] = i.Subject.subject_name
        homework[i.Day.day_id] = now

    # pick homework
    query = db_sess.query(Homework, Schedule, Day, Subject)
    query = query.join(Schedule, Schedule.schedule_id == Homework.homework_schedule)
    query = query.join(Day, Day.day_id == Schedule.schedule_day)
    query = query.join(Subject, Subject.subject_id == Schedule.schedule_subject)
    query = query.filter(Homework.homework_week == week, Homework.homework_year == year)

    for i in query.all():
        now = homework.get(i.Day.day_id, {})
        now[i.Schedule.schedule_num] = now.get(i.Schedule.schedule_num, {})
        now[i.Schedule.schedule_num]['subject_title'] = i.Subject.subject_name
        now[i.Schedule.schedule_num]['subject_homework'] = i.Homework.homework_text
        now[i.Schedule.schedule_num]['subject_file'] = i.Homework.homework_file
        homework[i.Day.day_id] = now
    days = db_sess.query(Day).all()

    first, last = get_start_and_end_date_from_calendar_week(year, week)

    return render_template('homework.html', title='Homework', days=days,
                           homework=homework, max_subjects=MAX_SUBJECTS,
                           year=str(year), week=str(week),
                           homework_start=first, homework_end=last)


@app.route('/homework/<int:year>/<int:week>/<int:day_num>', methods=['GET', 'POST'])
@login_required
def edit_homework(year, week, day_num):
    form = homework_forms.EditHomework()
    db_sess = db_session.create_session()
    day_name = db_sess.query(Day).filter(Day.day_id == day_num).first()
    if not day_name:
        abort(404)
    day_name = day_name.day_name

    if request.method == "GET":
        schedule = get_schedule(day_num)

        query = db_sess.query(Homework, Schedule, Subject)
        query = query.join(Schedule, Schedule.schedule_id == Homework.homework_schedule)
        query = query.join(Subject, Subject.subject_id == Schedule.schedule_subject)
        query = query.filter(Schedule.schedule_day == day_num)
        query = query.filter(Homework.homework_week == week)
        query = query.filter(Homework.homework_year == year)

        homework = query.all()
        for i in schedule:
            exec(f'form.subject_{i.Schedule.schedule_num}.label.text = "{i.Subject.subject_name}"')
        for i in homework:
            exec(f'form.subject_{i.Schedule.schedule_num}.default = "{i.Homework.homework_text}"')
        form.process()
        return render_template('homework_edit.html', title='Edit homework',
                               day_name=day_name, form=form)
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect('/homework')
        for subj_num in range(1, MAX_SUBJECTS + 1):
            schedule = get_schedule(day=day_num, subj_num=subj_num)[0]

            query = db_sess.query(Homework, Schedule)
            query = query.join(Schedule, Schedule.schedule_id == Homework.homework_schedule)
            query = query.filter(Schedule.schedule_day == day_num,
                                 Schedule.schedule_num == subj_num)
            query = query.filter(Homework.homework_week == week,
                                 Homework.homework_year == year)

            hmw = query.first()

            form_hmw = eval(f'form.subject_{subj_num}.data')
            form_hmw_file = eval(f'form.subject_{subj_num}_file.data')
            if form_hmw_file:
                trash, ext = os.path.splitext(form_hmw_file.filename)
                filename = f'{str(uuid.uuid4())}{ext}'
                filename = os.path.join(UPLOAD_FOLDER, filename)
                form_hmw_file.save(filename)
                form_hmw_file = filename
            else:
                form_hmw_file = None

            if hmw and (form_hmw or form_hmw_file):
                hmw.Homework.homework_text = form_hmw
                if form_hmw_file:
                    hmw.Homework.homework_file = form_hmw_file
            elif hmw and not form_hmw:
                hmw.Homework.homework_text = ''
                if form_hmw_file:
                    hmw.Homework.homework_file = form_hmw_file
            elif hmw is None and (form_hmw or form_hmw_file):
                new_hmw = Homework(homework_text=form_hmw, homework_schedule=schedule.Schedule.schedule_id,
                                   homework_year=year, homework_week=week, homework_file=form_hmw_file)
                db_sess.add(new_hmw)
        db_sess.commit()
        return redirect(f'/homework/{year}/{week}')


@app.route('/additional/dynamic/<string:filename>')
def show_file(filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)


if __name__ == 'app':
    app.register_blueprint(schedule_api.blueprint)
    app.register_blueprint(subjects_api.blueprint)
    app.register_blueprint(homework_api.blueprint)
    app.jinja_env.add_extension('jinja2.ext.do')
    login_manager.init_app(app)
    db_session.global_init("db/homework.db")
    app.run()
