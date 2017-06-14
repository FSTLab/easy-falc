$(document).ready(function() {


    // Remove paste formatting
    $('[id^=text-]').bind('paste', function(e){
        e.preventDefault();
        var text = e.originalEvent.clipboardData.getData('text');
        document.execCommand("insertHTML", false, text);
    });

    $('body').on('mouseenter', 'span[id^=warning-]', function(e) {
        var index = getCalloutIndex(this);
        showCallout(index, true);
    });

    $('body').on('mousemove', 'span[id^=warning-]', function(e) {
        var index = getCalloutIndex(this);
        setWarningsPosition(e.pageX, e.pageY);
    });

    $('body').on('mouseleave', 'span[id^=warning-]', function(e) {
        var index = getCalloutIndex(this);
        showCallout(index, false);
    });

    function getCalloutIndex(callout){
      return parseInt($(callout).attr("id").replace('warning-', ''), 10);
    }

    function setWarningsPosition(x, y) {
      $('#warnings-container').css({
            left: x + 10,
            top: y
        });
    }

    function showCallout(index, enters) {
      // it also highlights the text
        var callout = $("div[id=warning-" + index + "]");
        var spans = $("span[id=warning-" + index + "]");

        if (enters) {
            callout.removeClass("hide");
            spans.css('background-color', '#fdca40');
        } else {
            callout.addClass("hide");
            spans.css('background-color', '#ffe18f');
        }
    }

    var key_timeout0;
    var key_timeout1;

    $('#text-base').keydown(function() {
      clearTimeout(key_timeout0);
      key_timeout0 = setTimeout(function(){asyncTranslate('#text-base');}, 500);
    });

    $('#text-falc').keydown(function() {
      clearTimeout(key_timeout1);
      key_timeout1 = setTimeout(function(){asyncTranslate('#text-falc');}, 500);
    });

    function asyncTranslate(textarea){
      var text = $(textarea).text()
      $.ajax({
        url: '/translate',
        data: {
          'text': text
        },
        type: 'POST',
        success: function(response){
          var warnings = response['warnings'];
          var text = response['text'];
          update(text, warnings);
        }
      });
    }

    $('#button-summarize').click(function() {
      var text = $('#text-base').text();
      $.ajax({
        url: '/summarize',
        data: {
          'text': text
        },
        type: 'POST',
        success: function(response){
          var summary = response['summary'];
          var warnings = response['warnings'];
          update(summary, warnings);
        }
      })
    });

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
      var html_warnings = '';
      var html_summary = '';

      if(warnings.length > 0){
        html_summary += '<div class="callout">';
        html_summary += '<h5>Errors summary</h5>';
        html_summary += '<span class="badge alert">' + warnings.length + '</span> errors.';
        html_summary += '</div>';

        $.each(warnings, function(index, value){
          html_warnings += '<div class="callout alert hide" id="warning-' + index +'">';
          html_warnings += '<p id="warning-title">' + value['comment'] + '</p>';
          html_warnings += '<p class="warning-snippet"><i>' + value['snippet'] + '</i></p>';
          html_warnings += '</div>';
        });
      }else{
        html_summary += '<div class="callout success">';
        html_summary += '<p>Aucune problème rencontré</p>';
        html_summary += '</div>';
      }

      $('#warnings-container').html(html_warnings);
      $('#warnings-summary').html(html_summary);
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
