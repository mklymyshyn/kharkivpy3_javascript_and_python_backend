
(function () {
    var global = window.KHARKIVPY || {};
    var config = global.config || {};

    _.defaults(config, {
        'api_url': 'http://localhost/api/',
        'title': 'Sample Widget'
    });

    window.KHARKIVPY = global;
    window.KHARKIVPY.config = config;
})();

            var KHARKIVPYTPL = KHARKIVPYTPL || {};
            KHARKIVPYTPL._assign = function (obj, keyPath, value) {
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
        KHARKIVPYTPL._assign(KHARKIVPYTPL, ["main"], '<h1><%= title %></h1>');})();
(function () {

    $('#holder').html(
        _.template(KHARKIVPYTPL.main)({
            'title': KHARKIVPY.config.title
        })
    );

})();

(function (assets) {
    BrowserAssets('/static/', assets);
})({'Chrome': {'17': ['src/css/browsers/chrome17.css']}, 'Safari': {'5.1': ['src/css/browsers/safari5.css']}});
