$(document).ready(function() {
    tinymce.init({
        selector: 'textarea'
    });

    var tiny_ifr = $('#myta_ifr');

    tiny_ifr.contents().find("[id^=warning-]").mouseenter(function() {
        var index = parseInt($(this).attr("id").replace('warning-', ''), 10);
        highlight(index, true);
    });

    tiny_ifr.contents().find("[id^=warning-]").mouseleave(function() {
        var index = parseInt($(this).attr("id").replace('warning-', ''), 10);
        highlight(index, false);
    });

    $("[id^=warning-]").mouseenter(function() {
        var index = parseInt($(this).attr("id").replace('warning-', ''), 10);
        console.log("enters");
        highlight(index, true);
    });

    $("[id^=warning-]").mouseleave(function() {
        var index = parseInt($(this).attr("id").replace('warning-', ''), 10);
        console.log("leaves");
        highlight(index, false);
    });

    function highlight(index, enters) {
        var tiny_ifr = $('#myta_ifr');
        var a = tiny_ifr.contents().find("[id=warning-" + index + "]");
        var b = $("[id=warning-" + index + "]");
        if (enters) {
            a.css("background-color", "#fdca40");
            b.removeClass("hide");
        } else {
            a.css("background-color", "#ffe18f");
            b.addClass("hide");
        }
    }

    /*$("#myform").submit(function(event) {
		event.preventDefault();
		console.log($("#myta").val());
		$.ajax({
            url: "/action",
			method: "POST",
			data: $("#myta").val(),//only input
			dataType: "json",
            context: document.body
        }).done(function(data) {
			console.log(data)
            $(this).addClass("done");
        });

    });*/
});
