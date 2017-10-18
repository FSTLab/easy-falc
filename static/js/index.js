/**
 * index.js - EasyFALC
 *
 * Created by T. Roulin
 * 2017
 */


// Must always match doc TODO write doc
var Categories = {
  BAD : 0,
  ADVICE : 1,
  GOOD : 2
};
var CATEGORIES;
var TIPS;
var T;

function saveCategories(categories){
  CATEGORIES = categories;
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
    var text = $(textarea).text();
    $.ajax({
      url: '/translate',
      data: {
        'text': text
      },
      type: 'POST',
      success: function(response){
        update(response.text, response.tips);
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
        var summary = response.summary;
        var tips = response.tips;
        update(summary, tips);
      }
    });
  });

  /**
   * throws the update to the laoyut
   */
  function update(text, tips){
    $('#text-falc').html(generateText(text, tips));
    $('#warnings-summary').html(generateTips(tips));

    // Update foundation elements
    $(document).foundation();
    console.log("foundation updated");
  }


  /**
   * Format util for the text containers
   */
  function generateTextSpanBefore(index, tip, i){
    if(i == tip.start){
      return '<span id="warning-' + index + '" style="background-color: #ffe18f;">';
    }else{
      return '';
    }
  }

    /**
     * Format util for the text containers
     */
  function generateTextSpanAfter(tip, i){
    if(i == tip.end){
      return '</span>';
    }else{
      return '';
    }
  }

  function generateText(text, tips){
    var output = '';

    for(var i = 0, len = text.length; i < len; i++){
      for(var j = 0, lj = tips.length; j < lj; j++){
        output += generateTextSpanBefore(j, tips[j], i);
      }
      output += text[i];
      for(j = 0, lj = tips.length; j < lj; j++){
        output += generateTextSpanAfter(tips[j], i);
      }
    }
    return output;
  }

  function generateTips(tips){
    // Reset of t
    var t = {
      0: {},
      1: {},
      2: {}
    };

    // Classify tips
    $.each(tips, function(index, tip){
      var cid = tip.category_id;
      var p = CATEGORIES[cid].polarity;
      if(cid in t[p]){
        t[p][cid].push(tip);
      }else{
        t[p][cid] = [tip];
      }
    });

    //TODO remove (debug purpose)
    T = t;

    var dom = '';
    dom += generateTipsList('Améliorations possibles', t[Categories.BAD]);
    dom += generateTipsList('Conseils', t[Categories.ADVICE]);
    dom += generateTipsList('Bonnes pratiques', t[Categories.GOOD]);
    return dom;
  }

  function generateTipsList(title, tips){
    var dom = '';
    dom += '<h1>' + title + '</h1>';

    dom += '<ul class="accordion" data-accordion>';
    $.each(tips, function(index, tip){
      dom += '<li class="accordion-item" data-accordion-item>';
      dom += '<a href="#panel' + index + '" class="accordion-title">';
      dom += '<span class="badge">' + tip.length + '</span>';
      dom += CATEGORIES[index].title + '</a>';
      dom += '<div id="panel' + index + '" class="accordion-content" data-tab-content>';
      dom += 'We could display the snippets here';
      dom += '</div>';
      dom += '</li>';
    });
    return dom + '</ul>';
  }
});
