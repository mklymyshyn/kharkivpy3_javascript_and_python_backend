/*jslint indent: 4, nomen: false, sloppy: true, confusion: true */
(function () {
    // https://github.com/rsyring/browser-detect/
    var global = window.BrowserAssets || {};

    var BrowserDetect = {
        init: function () {
            this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
            this.version = this.searchVersion(navigator.userAgent)
                || this.searchVersion(navigator.appVersion)
                || "an unknown version";
            this.OS = this.searchString(this.dataOS) || "an unknown OS";
        },
        searchString: function (data) {
            for (var i=0;i<data.length;i++) {
                var dataString = data[i].string;
                var dataProp = data[i].prop;
                this.versionSearchString = data[i].versionSearch || data[i].identity;
                if (dataString) {
                    if (dataString.indexOf(data[i].subString) != -1)
                        return data[i].identity;
                }
                else if (dataProp)
                    return data[i].identity;
            }
        },
        searchVersion: function (dataString) {
            var index = dataString.indexOf(this.versionSearchString);
            if (index == -1) return;
            return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
        },
        dataBrowser: [
            // {
                // string: navigator.userAgent,
                // subString: "IE",
                // identity: "Internet Explorer"
            // },
            {
                string: navigator.vendor,
                subString: "Apple",
                identity: "Safari",
                versionSearch: "Version"
            },
            {
                string: navigator.vendor,
                subString: "Google",
                identity: "Chrome",
                versionSearch: "Chrome"
            },
            {
                prop: window.opera,
                identity: "Opera"
            },
            {
                string: navigator.userAgent,
                subString: "Firefox",
                identity: "Firefox"
            },
            {
                string: navigator.userAgent,
                subString: "MSIE",
                identity:  "IE", // important!, not "Explorer",
                versionSearch: "MSIE"
            },
            {
                string: navigator.userAgent,
                subString: "Gecko",
                identity: "Mozilla",
                versionSearch: "rv"
            },
            {
                string: navigator.userAgent,
                subString: "Mozilla",
                identity: "Netscape",
                versionSearch: "Mozilla"
            }
        ],
        dataOS : [
            {
                string: navigator.platform,
                subString: "Win",
                identity: "Windows"
            },
            {
                string: navigator.platform,
                subString: "Mac",
                identity: "Mac"
            },
            {
                string: navigator.userAgent,
                subString: "iPhone",
                identity: "iPhone/iPod"
            },
            {
                string: navigator.platform,
                subString: "Linux",
                identity: "Linux"
            }
        ]
    };
    BrowserDetect.init();

    var browser = BrowserDetect.OS + "-" +
        BrowserDetect.browser + "-" +
        BrowserDetect.version;

    // main method to load assets
    var loadAssets = function (host, files) {
        //document.write(browser);
        if (!(BrowserDetect.browser in files)) {
            return;
        }
        if (!(BrowserDetect.version in files[BrowserDetect.browser])) {
            return;
        }

        _.each(files[BrowserDetect.browser][BrowserDetect.version], function (file) {
            //document.write(file);
            include(host + file);
        });
    };

    window.BrowserAssets = loadAssets;
})();