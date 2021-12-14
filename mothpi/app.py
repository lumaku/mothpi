# !/usr/bin/python3
# -*- coding:utf-8 -*-

"""
Mothpi app

Run a web app to configure a mothpy instance.

2021, Technische Universität München, Ludwig Kürzinger
"""
import logging
from flask import Flask, render_template, flash, redirect
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, IntegerField, FloatField, StringField
from flask_nav import Nav
from flask_nav.elements import Navbar, View
import base64
import uuid

# Mothpi imports
from mothpi.config import config


def get_corresponding_field(key, value, description=None):
    # [int, float, str, bool]
    kwargs = {"label": key, "default": value, "description": description}
    if type(value) == int:
        field = IntegerField
    elif type(value) == float:
        field = FloatField
    elif type(value) == str:
        field = StringField
    elif type(value) == bool:
        field = BooleanField
        kwargs = {"label": description, "default": value}
    else:
        raise TypeError(f"Type of {value} not in [int, float, dict, str, bool].")
    return field(**kwargs)


def create_app():
    # We are using the "Application Factory"-pattern here, which is described
    # in detail inside the Flask docs:
    # http://flask.pocoo.org/docs/patterns/appfactories/
    app = Flask(__name__)
    logging.info("Started flask server")
    secret_token = uuid.uuid4().hex
    app.config["SECRET_KEY"] = secret_token
    logging.info(f"Secret app token: {secret_token}")

    # Navigation
    nav = Nav()

    @nav.navigation()
    def mynavbar():
        return Navbar(
            "Mothpi Web App",
            View("Main", ".index"),
            View("Configuration", ".configuration_page"),
        )

    # Shows a long signup form, demonstrating form rendering.
    @app.route("/")
    def index():
        # Status image
        status_image = (
            "/home/kue/pics/epaper_display.png"  # config.get_status_img_path()
        )
        with open(status_image, "rb") as f:
            status_image = f.read()
        status_image = "data:image/png;base64," + base64.b64encode(status_image).decode(
            "utf-8"
        )
        # Base64 encoding looks like this:
        # status_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="

        return render_template("index.html", status_image=status_image)

    # Shows a long signup form, demonstrating form rendering.
    @app.route("/config", methods=("GET", "POST"))
    def configuration_page():
        # Config form with dynamic fields
        class ConfigForm(FlaskForm):
            submit_button = SubmitField("Save Changes to Configuration")

        for key, value, description in config.get_descriptive_list():
            setattr(
                ConfigForm,
                key,
                get_corresponding_field(key, value, description=description),
            )
        change_dict = {key: value for key, value, _ in config.get_descriptive_list()}

        form = ConfigForm()
        if form.validate_on_submit():
            for item in change_dict:
                x = getattr(form, item)
                change_dict[item] = x.data
                print(f"{item}={x.data}")
            success = config.update_from_dict(change_dict)
            config.save_config()
            if success:
                flash("Configuration saved! (success)", "info")
            else:
                flash("Update partially successful - Check your values", "error")
            return redirect("/config")
        return render_template("config.html", form=form)

    nav.init_app(app)
    Bootstrap(app)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
