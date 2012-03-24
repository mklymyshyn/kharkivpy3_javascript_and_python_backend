
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