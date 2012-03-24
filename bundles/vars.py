
from webassets.filter import Filter, register_filter
from webassets.filter import get_filter
from flaskext.assets import Bundle


__all__ = ('VarsFilter', 'JSVarsBundle',)


class VarsFilter(Filter):

    name = 'vars'

    def __init__(self, *args, **kwargs):
        self.vars = kwargs.pop('vars')
        super(VarsFilter, self).__init__(*args, **kwargs)

    def replace(self, _in):
        data = _in.read()

        for key, val in self.vars.iteritems():
            data = data.replace('$$%s' % key, val)
        return data

    def input(self, _in, out, source_path, output_path):
        out.write(self.replace(_in))


class JSVarsBundle(Bundle):
    """Bundle to replace variables within
    JavaScript source files in realtime
    """
    def __init__(self, *args, **kwargs):
        ignore_filters = kwargs.pop('ignore_filters', False) or False
        kwargs['debug'] = False

        try:
            filters = list(kwargs.pop('filters'))
        except KeyError:
            filters = []

        try:
            vars = kwargs.pop('vars')
        except KeyError:
            vars = {}

        fltr = get_filter('vars', vars=vars)

        if not ignore_filters:
            filters.extend([fltr])
        else:
            filters = fltr

        kwargs.update({
            'filters': filters
        })

        Bundle.__init__(self, *args, **kwargs)

    def resolve_contents(self, *args, **kwargs):
        c = super(JSVarsBundle, self).resolve_contents(*args, **kwargs)
        print "Resolved: ", c
        return c

    def _build(self, *args, **kwargs):
        """We just set force parameter to
        true and call parent _build method"""
        kwargs['force'] = True
        Bundle._build(self, *args, **kwargs)


register_filter(VarsFilter)
