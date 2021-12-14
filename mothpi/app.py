# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi app

Run a web app to configure a mothpy instance.

2021, Technische Universität München, Ludwig Kürzinger
"""
import logging

from flask import Flask, render_template, flash, redirect, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import TextField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FloatField, StringField, validators
from wtforms.validators import DataRequired
from flask_nav import Nav
from flask_nav.elements import Navbar, View

import base64
from pathlib import Path

# Mothpi imports
from mothpi.config import MothConf

# TODO Global!!
config = MothConf()
config_dict = config.get_dict()


def get_corresponding_field(key, value, description=None):
    # [int, float, str, bool]
    if type(value) ==  int:
        field = IntegerField
    elif type(value) == float:
        field = FloatField
    elif type(value) == str:
        field = StringField
    elif type(value) == bool:
        field = BooleanField
    else:
        raise TypeError(f"Type of {value} not in [int, float, dict, str, bool].")
    return field(key, default=value, description=description)

class ConfigForm(FlaskForm):
    """Configuration form.

    Here, each entry of the configuration has a field.
    """
    submit_button = SubmitField('Save Changes to Configuration')


# add dynamic fields
for key, value, description in config.get_descriptive_list():
    setattr(ConfigForm, key, get_corresponding_field(key, value, description=description))


def create_app():
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/
    app = Flask(__name__)
    # in a real app, these should be configured through Flask-Appconfig
    app.config['SECRET_KEY'] = 'devkey'
    app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'
    app.config['UPLOAD_FOLDER'] = config.pictures_save_folder

    # Navigation
    nav = Nav()

    @nav.navigation()
    def mynavbar():
        return Navbar(
            'Mothpi Web App',
            View('Main', '.index'),
            View('Configuration', '.configuration_page'),
        )

    # Shows a long signup form, demonstrating form rendering.
    @app.route('/')
    def index():
        # Status image
        status_image = "/home/kue/pics/epaper_display.png" # config.get_status_img_path()
        with open(status_image,'rb') as f:
            status_image = f.read()
        status_image = "data:image/png;base64," + base64.b64encode(status_image).decode('utf-8')
        # status_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="

        return render_template('index.html', status_image=status_image )

    # Shows a long signup form, demonstrating form rendering.
    @app.route('/config', methods=('GET', 'POST'))
    def configuration_page():
        form = ConfigForm()
        if form.validate_on_submit():
            flash('Configuration saved! (success)', 'info')
            return redirect('/config')
        return render_template('config.html', form=form)

    nav.init_app(app)
    Bootstrap(app)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)

