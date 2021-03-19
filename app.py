from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_restful import Api, abort

from data import db_session
from data.users import User
from data.days import Day
from data.schedules import Schedule
from data.subjects import Subject
from data.homework import Homework

from forms import user_forms, schedule_forms

from constants import MAX_SUBJECTS

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
app.config['SECRET_KEY'] = '267iokdonibf890wi4k23ioruh8fuipokaldfsa'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def hello_world():
    return render_template('base.html', title='Hi')


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


@app.route('/schedule')
def schedule():
    db_sess = db_session.create_session()
    schedule = {}
    query = db_sess.query(Schedule, Day, Subject)
    query = query.join(Day, Day.day_id == Schedule.schedule_day)
    query = query.join(Subject, Subject.subject_id == Schedule.schedule_subject)

    for i in query.all():
        now = schedule.get(i.Day.day_id, {})
        schedule[i.Day.day_id] = now
        now[i.Schedule.schedule_num] = i.Subject.subject_name
        schedule[i.Day.day_id] = now
    days = db_sess.query(Day)
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
    subj = [i.subject_name for i in db_sess.query(Subject).order_by(Subject.subject_name).all()]
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


if __name__ == 'app':
    app.jinja_env.add_extension('jinja2.ext.do')
    login_manager.init_app(app)
    db_session.global_init("db/homework.db")
    app.run()
