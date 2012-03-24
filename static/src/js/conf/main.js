
(function () {
    var global = window.KHARKIVPY || {};
    var config = global.config || {};

    _.defaults(config, {
        'api_url': '$$API_URL',
        'title': '$$TITLE'
    });

    window.KHARKIVPY = global;
    window.KHARKIVPY.config = config;
})();