var CATEGORIES;

function saveCategories(categories){
  CATEGORIES = categories;
  console.log(CATEGORIES);
}

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
        var tips = response['tips'];
        var text = response['text'];
        update(text, tips);
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
        var tips = response['tips'];
        update(summary, tips);
      }
    })
  });

  function update(text, tips){
    generateText(text, tips);
    generateTips(tips);
  }


  function generateText(text, tips){
    var c = $('#text-falc');

    var output = '';

    for(var i = 0, len = text.length; i < len; i++){

      $.each(tips, function(index, value){
        if (i == value['start']){
          output += '<span id="warning-' + index + '" \
          style="background-color: #ffe18f;">';
        }
      });

      output += text[i];

      $.each(tips, function(index, value){
        if (i == value['end']){
          output += '</span>';
        }
      });
    }

    c.html(output);

  }


  function generateTips(tips){

    var t = {}

    // Classify tips
    $.each(tips, function(index, tip){
      t[CATEGORIES[tip['category_id']].polarity] = tips;
    });

    var html = '';

    html += '<b>Améliorations possibles:</b><br />';
    $.each(t[0], function(index, tip){
      html += CATEGORIES[tip['category_id']]
    });



    // $('#warnings-container').html(html_warnings);
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
