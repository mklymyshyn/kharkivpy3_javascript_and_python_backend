import json

from flaskext.assets import Bundle
from webassets.filter import Filter, register_filter
from webassets.bundle import is_url
from webassets.merge import (make_url, merge_filters,
    FileHunk, MemoryHunk, UrlHunk, apply_filters, merge,
    make_url, merge_filters)


__all__ = (
    'BrowserBundle', 'LoaderBrowserBundle', 'LoaderBrowserFilter'
)

LOADER_SCRIPT = '''
(function (assets) {
    BrowserAssets('%s', assets);
})(%s);
'''


class BrowserBundle(Bundle):
    def __init__(self, *args, **kwargs):
        self.browser = kwargs.pop('browser', '')
        self.browser_version = kwargs.pop('browser_version', '')
        Bundle.__init__(self, *args, **kwargs)


class LoaderBrowserBundle(Bundle):
    """
    Generate js file which will load js/css file associated with
    user browser.
    Js file contain sets of js/css files from all ``BroswerBundle``
    """
    def __init__(self, *args, **kwargs):
        self.bundles = kwargs.pop('bundles', [])

        # for arg in args:
        #     if isinstance(arg, BrowserBundle):
        #         self.bundles.append(arg)
        Bundle.__init__(self, *args, **kwargs)

    def _build(self, *args, **kwargs):
        """We just set force parameter to true and call parent _build method"""
        kwargs['force'] = True
        Bundle._build(self, *args, **kwargs)

    def _merge_and_apply(self, env, output_path, force, parent_debug=None,
                         parent_filters=[], extra_filters=[],
                         disable_cache=False):

        debug = reduce(lambda x, y: x if not x is None else y,
            [self.debug, parent_debug, env.debug])
        if debug == 'merge':
            no_filters = True
        elif debug is True:
            no_filters = False
        elif debug is False:
            no_filters = False
        else:
            raise BundleError('Invalid debug value: %s' % debug)

        # Prepare contents
        resolved_contents = self.resolve_contents(env, force=True)

        if not resolved_contents:
            raise BuildError('empty bundle cannot be built')

        # Prepare filters
        filters = merge_filters(self.filters, extra_filters)
        for filter in filters:
            if isinstance(filter, LoaderBrowserFilter):
                filter.set_environment(env, bundle=self)
            else:
                filter.set_environment(env)

        # Apply input filters to all the contents. Note that we use
        # both this bundle's filters as well as those given to us by
        # the parent. We ONLY do those this for the input filters,
        # because we need them to be applied before the apply our own
        # output filters.
        combined_filters = merge_filters(filters, parent_filters)
        hunks = []
        for _, c in resolved_contents:
            if isinstance(c, Bundle):
                hunk = c._merge_and_apply(
                    env, output_path, force, debug,
                    combined_filters, disable_cache=disable_cache)
                hunks.append(hunk)
            else:
                if is_url(c):
                    hunk = UrlHunk(c)
                else:
                    hunk = FileHunk(c)
                if no_filters:
                    hunks.append(hunk)
                else:
                    hunks.append(apply_filters(
                        hunk, combined_filters, 'input',
                        env.cache, disable_cache,
                        output_path=output_path))

        # Return all source hunks as one, with output filters applied
        try:
            final = merge(hunks)
        except IOError, e:
            raise TypeError(e)

        if no_filters:
            return final
        else:
            return apply_filters(final, filters, 'output',
                                 env.cache, disable_cache)

    def _urls(self, env, extra_filters, *args, **kwargs):
        # Resolve debug: see whether we have to merge the contents
        debug = self.debug if self.debug is not None else env.debug
        if debug == 'merge':
            supposed_to_merge = True
        elif debug is True:
            supposed_to_merge = True
        elif debug is False:
            supposed_to_merge = True
        else:
            raise TypeError('Invalid debug value: %s' % debug)

        if supposed_to_merge and (self.filters or self.output):
            # We need to build this bundle, unless a) the configuration
            # tells us not to ("supposed_to_merge"), or b) this bundle
            # isn't actually configured to be built, that is, has no
            # filters and no output target.
            hunk = self._build(env, extra_filters=extra_filters,
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
                    urls.append(make_url(env, c, expire=False))
            return urls


class LoaderBrowserFilter(Filter):
    name = 'loader_browser'

    def set_environment(self, env, bundle=None):
        """
        This is called just before the filter is used.
        """
        if not self.env or self.env != env:
            self.env = env
            if bundle:
                self.setup(bundle=bundle)
            else:
                self.setup()

    def setup(self, bundle=None):
        self.bundle = bundle

    def input(self, _in, out, *args, **kwargs):
        output = {}
        files = []
        to_write = ''

        for bundle in self.bundle.bundles:
            if self.env.debug:
                files = bundle.contents
            else:
                files = [bundle.output]

            if bundle.browser not in output:
                output.update({bundle.browser: {}})

            if bundle.browser_version not in \
                output[bundle.browser]:
                output[bundle.browser].update({bundle.browser_version: []})
            output[bundle.browser][bundle.browser_version] += files

            # TODO: refactor it to use flask's app
            # variables
            if  self.env.app.config.get("ASSETS_DEBUG"):
                cdn = self.env.app.static_url_path + "/"
            else:
                if not self.env.app.config.get('ASSETS_CDN', False):
                    cdn = self.env.app.static_url_path
                else:
                    cdn = self.env.app.config.get('ASSETS_CDN')

            # build init script
            # TODO: refactor to use something standartized
            to_write = LOADER_SCRIPT % (
                cdn, output
            )

        out.write(to_write)

    def output(self, _in, out, **kwargs):
        out.write(_in.read())

register_filter(LoaderBrowserFilter)
