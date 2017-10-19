/*jshint esversion: 6*/

/**
 * index.js - EasyFALC
 *
 * Created by T. Roulin
 * 2017
 */


/*************************************\
| ************* STATICS ************* |
\*************************************/
var Categories = {
  BAD : 0,
  ADVICE : 1,
  GOOD : 2
};
var CATEGORIES;
var TIPS;
var T;

var TA_BASE = '#text-base';
var TA_EDIT = '#text-edit';
var TEXTAREAS = [TA_BASE, TA_EDIT];
var ALL_TAS = TEXTAREAS.join(',');

var lastEditedTextarea = TA_BASE;


/*************************************\
| ************** UTILS ************** |
\*************************************/

/**
 * Save the categories.
 *
 * @param categories : A dict of every possible tip category.
 */
function saveCategories(categories){
  CATEGORIES = categories;
}

/**
 * Check if an object is empty. An object is empty if it has no key.
 *
 * @param obj The object we were talking about.
 */
function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}


/*************************************\
| ************** ASYNC ************** |
\*************************************/

function asyncTranslate(textarea){
  var text = $(textarea).text();
  $.ajax({
    url: '/translate',
    data: {
      'text': text
    },
    type: 'POST',
    success: function(response){
      update(textarea, response.text, response.tips);
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
      update('#text-falc', response.summary, response.tips);
    }
  });
});

/**
 * throws the update to the laoyut
 */
function update(textarea, text, tips){
  TIPS = tips;

  $(textarea).html(generateFormattedText(text, tips));
  $('#tips-container').html(generateTips(tips));

  // Update foundation elements (like accordion)
  $(document).foundation();
}

/*************************************\
| ********** Generate HTML ********** |
\*************************************/

/**
 * Format util for the text containers
 */
function generateTextSpanBefore(index, tip, i){
  if(i == tip.start){
    return '<span id="warning-' + index + '">';
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


function generateFormattedText(text, tips){
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
    tip.index = index;
    if(cid in t[p]){
      t[p][cid].push(tip);
    }else{
      t[p][cid] = [tip];
    }
  });

  //TODO remove (debug purpose)
  T = t;

  var html = '';
  html += generateTipsByPolarity('Améliorations possibles', t[Categories.BAD]);
  html += generateTipsByPolarity('Conseils', t[Categories.ADVICE]);
  html += generateTipsByPolarity('Bonnes pratiques', t[Categories.GOOD]);
  return html;
}

function generateTipsByPolarity(title, tips_by_polarity){
  console.log(tips_by_polarity);
  if(isEmpty(tips_by_polarity)){
    return '';
  }

  var html = '';
  html += '<h3>' + title + '</h3>';
  html += '<ul class="accordion" data-accordion>';
  html += Object.entries(tips_by_polarity).map(entry => generateTipsByCategory(entry)).join('');
  html += '</ul>';

  return html;
}

function generateTipsByCategory(entry){
  var index = entry[0];
  var tips = entry[1];

  var html = '';
  html += '<li class="accordion-item" data-accordion-item>';
  html += '<a href="#panel' + index + '" class="accordion-title">';
  html += '<span class="badge">' + tips.length + '</span>';
  html += CATEGORIES[index].title + '</a>';
  html += '<div id="panel' + index + '" class="accordion-content" data-tab-content>';
  html += tips.map(tip => generateTip(tip)).join('');
  html += '</div>';
  html += '</li>';
  return html;
}

function generateTip(tip){
  var html = '';
  html += '<div class="tip-' + tip.index + '">' + tip.snippet + '</div>';
  return html;
}

/*************************************\
| ********* onDocumentReady ********* |
\*************************************/
$(document).ready(function() {
  // Remove paste formatting
  $(ALL_TAS).bind('paste', function(e){
    e.preventDefault();
    var text = e.originalEvent.clipboardData.getData('text');
    document.execCommand("insertHTML", false, text);
  });

  // $('body').on('mouseenter', 'span[id^=warning-]', function(e) {
  //   var index = getCalloutIndex(this);
  //   showCallout(index, true);
  // });
  //
  // $('body').on('mousemove', 'span[id^=warning-]', function(e) {
  //   var index = getCalloutIndex(this);
  //   setWarningsPosition(e.pageX, e.pageY);
  // });
  //
  // $('body').on('mouseleave', 'span[id^=warning-]', function(e) {
  //   var index = getCalloutIndex(this);
  //   showCallout(index, false);
  // });
  //
  // function getCalloutIndex(callout){
  //   return parseInt($(callout).attr("id").replace('warning-', ''), 10);
  // }

  function highlightTip(index, enters) {
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

  var key_timeout;
  $('div[id^=text-]').on('input focus', function(event) {
    clearTimeout(key_timeout);
    key_timeout = setTimeout(function(){
      asyncTranslate('#' + event.target.id);
    }, 500);
  });

});
