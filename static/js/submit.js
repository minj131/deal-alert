$(function () {
     $("#form").submit(function (event) {
        event.preventDefault();
        const _this = $(this);
        $("#button").addClass("onclic", 250, validate(_this));
    });

    function validate(th) {
        setTimeout(function () {
            $("#button").removeClass("onclic");
            $("#button").addClass("validate", 450, callback(th));
        }, 2250);
    }
    function callback(th) {
        setTimeout(function () {
            $("#button").removeClass("validate");
        }, 1250);
        th.unbind('submit').submit();
    }
});