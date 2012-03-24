from flask import url_for

from flask.ext.assets import Bundle

from bundles.scss_bundle import register_scss_bundle
from bundles.vars import JSVarsBundle
from bundles.jstemplates import register_template_bundle
from bundles.browsers import BrowserBundle, LoaderBrowserBundle


def constants(app):
    """
    Generate settings for JavaScript source files
    """
    cfg = {}
    with app.test_request_context():
        cfg.update(dict(
            API_URL=url_for("api", _external=True),
            TITLE="Sample Widget"
        ))

    return cfg


def register(app, assets):

    # JS core
    core = Bundle(
        "src/js/lib/core/*.js",
        "src/js/lib/*.js",
        output="js/core.js"
    )

    assets.register("js_core", core)

    # JS Source Files
    conf_app = JSVarsBundle(
        "src/js/conf/main.js",
        output="js/compiled/conf/conf.js",
        vars=constants(app),
        #filters=['yui_js"],
        ignore_filters=assets.debug
    )

    assets.register("js_conf", conf_app)

    # JS Source Files
    client_app = Bundle(
        "src/js/*.js",
        output="js/compiled/app.js",
    )

    assets.register("js_app", client_app)

    # Styles
    style_files = (
        'reset.scss',
        'base.scss',
    )

    register_scss_bundle(
        style_files,
        assets=assets,
        name='css_core',
        output='css/style.css',
        prefix='src/css',
        compile_to='css/compiled'
    )

    # Templates
    templates = (
        '*.tpl',
    )

    register_template_bundle(
        templates,
        namespace='KHARKIVPYTPL',
        name='js_templates',
        output='js/compiled/_templates.js',
        assets=assets
    )

    # custom CSS for different browsers
    chrome17 = BrowserBundle(
        'src/css/browsers/chrome17.css',
        browser='Chrome',
        browser_version='17',
        output='css/chrome17.css'
    )

    safari5 = BrowserBundle(
        'src/css/browsers/safari5.css',
        browser='Safari',
        browser_version='5.1',
        output='css/safari5.css'
    )

    assets.register("chrome17", chrome17)
    assets.register("safari5", safari5)

    browserspec_assets_loader = LoaderBrowserBundle(
        'src/css/browsers/safari5.css',
        bundles=[
           chrome17,
           safari5,
        ],
        filters='loader_browser',
        output='js/compiled/assets-loader.js'
    )

    assets.register("browserspec_assets_loader", browserspec_assets_loader)

    # build app
    app_build = Bundle(
        "src/js/compiled/conf/*.js",
        "src/js/compiled/*.js",
        "js/compiled/assets-loader.js",
        output='js/app.js'
    )

    assets.register("js", app_build)
