from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User, Subject, Chapter, Quiz, Questions, Scores, Enrollments
from functools import wraps

bp_main=Blueprint('main',__name__)

@bp_main.route('/')
def home():
    return render_template('index.html')