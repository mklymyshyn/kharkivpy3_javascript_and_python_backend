import os
import urlparse
import scss

from flaskext.assets import Bundle
from webassets.filter import Filter, register_filter

from webassets.merge import make_url


__all__ = (
    'SCSSBundle',
    'SCSSFilter',
    'register_scss_bundle',
)


def is_url(s):
    if not isinstance(s, str):
        return False
    scheme = urlparse.urlsplit(s).scheme
    return bool(scheme) and len(scheme) > 1


def save_css(filename, data):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    f = open(filename, 'wb')
    try:
        f.write(data)
    finally:
        f.close()


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


class SCSSBundle(Bundle):
    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix')

        self.compile_dir = kwargs.pop('compile_dir')
        self.prefix = prefix

        args = [os.path.join(prefix, el) for el in args]
        Bundle.__init__(self, *args, **kwargs)

    def _build(self, *args, **kwargs):
        """We just set force parameter to true and call parent _build method"""
        kwargs['force'] = True
        Bundle._build(self, *args, **kwargs)

    def _urls(self, env, extra_filters, *args, **kwargs):
        # Resolve debug: see whether we have to merge the contents
        debug = self.debug if self.debug is not None else env.debug
        if debug == 'merge':
            supposed_to_merge = True
        elif debug is True:
            supposed_to_merge = False
        elif debug is False:
            supposed_to_merge = True
        else:
            raise TypeError('Invalid debug value: %s' % debug)

        if supposed_to_merge and (self.filters or self.output):
            # We need to build this bundle, unless a) the configuration
            # tells us not to ("supposed_to_merge"), or b) this bundle
            # isn't actually configured to be built, that is, has no
            # filters and no output target.
            self._build(env, extra_filters=extra_filters,
                               *args, **kwargs)
            return [make_url(env, self.output)]
        else:
            # We either have no files (nothing to build), or we are
            # in debug mode: Instead of building the bundle, we
            # source all contents instead.
            urls = []
            for c, _ in self.resolve_contents(env):
                if isinstance(c, Bundle):
                    urls.extend(c.urls(env, *args, **kwargs))
                else:
                    css_file = self.create_css(c)
                    urls.append(make_url(env, css_file, expire=False))
            return urls

    def create_css(self, path_to_scss):
        scss_path = path_to_scss.replace(self.prefix, '')[1:]
        rel_path = os.path.dirname(scss_path)
        css_path = os.path.join(self.compile_dir,
            scss_path.replace('scss', 'css'))
        abs_css_path = self.env.abspath(css_path)
        css = scss.Scss(scss_opts={
            'debug_info': False,
            'verbosity': 0,
        })
        result = css.compile(scss_file=self.env.abspath(path_to_scss))
        save_css(abs_css_path, result)
        return os.path.join(self.compile_dir, rel_path,
            abs_css_path.split('/')[-1])


class SCSSFilter(Filter):
    name = 'scssfilter'

    def setup(self):
        self.compiled = {}

    def input(self, _in, out, source_path, output_path):
        css = scss.Scss(scss_opts={
            'debug_info': False,
            'verbosity': 0,
        })
        result = css.compile(scss_file=source_path)
        out.write(result)

    def output(self, _in, out, **kwargs):
        out.write(_in.read())


def register_scss_bundle(scss,
        assets=None,
        output=None,
        prefix='',
        compile_to='',
        name=''):
    """
    Function to automate registartion
    SCSS bundles
    """
    SCSSFilter.base_assets_dir = assets.directory
    SCSSFilter.base_scss_dir = os.path.join(
        SCSSFilter.base_assets_dir,
        prefix
    )

    register_filter(SCSSFilter)

    widget_scss = SCSSBundle(
        *scss,
        compile_dir=compile_to,
        filters='scssfilter',
        output=output,
        prefix=prefix
    )

    assets.register(name, widget_scss)

    return widget_scss
