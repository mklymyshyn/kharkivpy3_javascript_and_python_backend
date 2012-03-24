from flask import Flask, render_template

from flask.ext.assets import Environment
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from assets import register as register_assets


app = Flask(__name__)

app.config.update(
    DEBUG=True,
    ASSETS_DEBUG=True

)


# views
@app.route('/')
def home():
    return render_template(
        "base.html",
        debug=app.config.get("ASSETS_DEBUG")
    )


@app.route('/api/')
def api():
    return ''


# install Flask-Assets
assets = Environment(app)
register_assets(app, assets)

# define management commands
manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))

if __name__ == '__main__':

    manager.run()
