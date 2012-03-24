(function () {
    var init = function () {
        console.log(KHARKIVPYTPL);
        return;
        $('#holder').html(
            _.template(KHARKIVPY.main)({
                'title': KHARKIVPY.title
            })()
        );
    };

    init();
})();