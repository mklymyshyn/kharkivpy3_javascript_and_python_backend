import os
import string
import json
from flaskext.assets import Bundle
from webassets.filter import Filter, register_filter


__all__ = ('register_template_bundle', )


UNDERSCORE_TEMPLATES_DIR = 'src/templates/'


class TemplatesAssetError(Exception):
    pass


class TemplateFilter(Filter):
    name = 'underscore_templates'

    def setup(self):
        self.compiled = []
        self.namespace = "KHARKIVPYTPL"
        self.before = """
            var %(namespace)s = %(namespace)s || {};
            %(namespace)s._assign = function (obj, keyPath, value) {
               var lastKeyIndex = keyPath.length - 1;
               for (var i = 0; i < lastKeyIndex; i++) {
                    key = keyPath[i];
                    if (typeof obj[key] === "undefined") {
                        obj[key] = {};
                    }
                    obj = obj[key];
                }
                obj[keyPath[lastKeyIndex]] = value;
            };
            (function(){
        """ % {'namespace': self.namespace}
        self.after = "})();"
        self.extension = ".tpl"

    def namespace_list(self, source_path):
        alphanumeric = string.letters + string.digits
        good_path_chars = alphanumeric + os.path.sep
        relpath = os.path.relpath(source_path, self.base_templates_dir)
        if relpath.endswith(self.extension):
            relpath = relpath[:-len(self.extension)]
        if set(relpath) - set(good_path_chars):
            raise TemplatesAssetError('bad templates path: %r' % relpath)
        return relpath.split(os.path.sep)

    def input(self, _in, out, source_path, output_path):
        nl = self.namespace_list(source_path)
        fmt = "%(namespace)s._assign(%(namespace)s, %(path)s, '%(template)s');"
        item = {
            'namespace': self.namespace,
            'template': _in.read().replace('\n', '').replace("'", r"\'"),
            'path': json.dumps(nl),
        }
        self.compiled.append(fmt % item)

    def output(self, _in, out, **kw):
        output = self.before + "".join(self.compiled) + self.after
        out.write(output)


class AlwaysUpdatedBundle(Bundle):
    def __init__(self, *args, **kwargs):
        kwargs['debug'] = False
        args = [os.path.join(UNDERSCORE_TEMPLATES_DIR, el) for el in args]
        Bundle.__init__(self, *args, **kwargs)

    def _build(self, *args, **kwargs):
        """We just set force parameter to true and call parent _build method"""
        kwargs['force'] = True
        Bundle._build(self, *args, **kwargs)


def register_template_bundle(files,
        namespace='KHARKIVPYTPL',
        name=None, output=None, assets=None
        ):
    TemplateFilter.base_assets_dir = assets.directory
    TemplateFilter.namespace = namespace,
    TemplateFilter.base_templates_dir = os.path.join(
                                            TemplateFilter.base_assets_dir,
                                            UNDERSCORE_TEMPLATES_DIR
                                        )
    register_filter(TemplateFilter)

    filters = ['underscore_templates']

    widget_templates = AlwaysUpdatedBundle(
        *files,
        filters=filters,
        output=output

    )

    assets.register(name, widget_templates)
    return widget_templates
