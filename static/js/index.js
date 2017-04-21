$(document).ready(function() {

    $('body').on('mouseenter', 'span[id^=warning-]', function(e) {
        var index = parseInt($(this).attr("id").replace('warning-', ''), 10);
        console.log("enters");
        highlight(index, true);
    });

        $('body').on('mouseleave', 'span[id^=warning-]', function(e) {
        var index = parseInt($(this).attr("id").replace('warning-', ''), 10);
        console.log("leaves");
        highlight(index, false);
    });

    function highlight(index, enters) {
        var divs = $("div[id=warning-" + index + "]");
        var spans = $("span[id=warning-" + index + "]");
        if (enters) {
            divs.removeClass("hide");
            spans.css('background-color', '#fdca40');
        } else {
            divs.addClass("hide");
            spans.css('background-color', '#ffe18f');
        }
    }

    var key_timeout;

    $('#text-base').keypress(function() {
      clearTimeout(key_timeout);
      key_timeout = setTimeout(doShit, 500);
    });

    function doShit(){
      var text_base = $('#text-base').text()
      $.ajax({
        url: '/translate',
        data: {
          'text-base': text_base
        },
        type: 'POST',
        success: function(response){
          var warnings = response['warnings'];
          var text = response['text'];
          console.log(warnings);
          update(text, warnings);
        }
      });
    }

    function update(text, warnings){
      generateText(text, warnings);
      generateWarnings(warnings);
    }


    function generateText(text, warnings){
      var c = $('#text-falc');

      var output = '';

      for(var i = 0, len = text.length; i < len; i++){

        $.each(warnings, function(index, value){
          if (i == value['start']){
            output += '<span id="warning-' + value['index'] + '" \
                      style="background-color: #ffe18f;">';
          }
        });

        output += text[i];

        $.each(warnings, function(index, value){
          if (i == value['end']){
            output += '</span>';
          }
        });
      }

      c.html(output);

    }


    function generateWarnings(warnings){
      var output = '';

      if(warnings.length > 0){
        output += '<div class="callout">';
        output += '<h5>Errors summary</h5>';
        output += '<span class="badge alert">' + warnings.length + '</span> errors.';
        output += '</div>';

        $.each(warnings, function(index, value){
          output += '<div class="callout alert hide" id="warning-' + index +'">';
          output += '<p>' + value['comment'] + '</p>';
          output += '<p class="warning-snippet"><i>' + value['snippet'] + '</i></p>';
          output += '</div>';
        });
      }else{
        output += '<div class="callout success">';
        output += '<p>Aucune problème rencontré</p>';
        output += '</div>';
      }

      $('#warnings-container').html(output);
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
