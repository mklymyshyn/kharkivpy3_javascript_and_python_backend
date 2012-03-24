(function () {

    $('#holder').html(
        _.template(KHARKIVPYTPL.main)({
            'title': KHARKIVPY.config.title
        })
    );

})();