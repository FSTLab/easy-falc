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

var lastXhrRequest = null;


/*************************************\
| ************** UTILS ************** |
\*************************************/
/**
 * A linear interpolator for hexadecimal colors
 * @param {String} a
 * @param {String} b
 * @param {Number} amount
 * @example
 * // returns #7F7F7F
 * lerpColor('#000000', '#ffffff', 0.5)
 * @returns {String}
 */
function lerpColor(a, b, amount) {

    var ah = parseInt(a.replace(/#/g, ''), 16),
        ar = ah >> 16, ag = ah >> 8 & 0xff, ab = ah & 0xff,
        bh = parseInt(b.replace(/#/g, ''), 16),
        br = bh >> 16, bg = bh >> 8 & 0xff, bb = bh & 0xff,
        rr = ar + amount * (br - ar),
        rg = ag + amount * (bg - ag),
        rb = ab + amount * (bb - ab);

    return '#' + ((1 << 24) + (rr << 16) + (rg << 8) + rb | 0).toString(16).slice(1);
}

function lerpMultipleColor(colors, t){
  if(t==1){
    return colors[colors.length - 1];
  }

  let scaledT = t * (colors.length - 1);
  let prevC = colors[parseInt(scaledT)];
  let nextC = colors[parseInt(scaledT + 1)];
  let newT = scaledT - parseInt(scaledT);
  return lerpColor(prevC, nextC, newT);
}


/**
 * Util to easily get a tip polarity.
 *
 * TODO Maybe with a better implementation it wouldn't need This
 * complexity. But it might need redundancy.
 */
function getTipPolarity(tip){
  return CATEGORIES[tip.category_id].polarity;
}

/**
 * Utils to get text from a polarity integer.
 *
 * TODO l2c
 */
function getPolarityText(polarity){
  switch(polarity){
    case Categories.BAD:
      return "bad";
    case Categories.ADVICE:
      return "advice";
    case Categories.GOOD:
      return "good";
  }
}

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

/**
 * Save the current caret position in the specified context.
 *
 * This returns an integer that is intended to use with
 * the restoreCaretPosition(context, caretPos) method as caretPos.
 * Source: https://stackoverflow.com/a/38479462
 *
 * @param context Html element selector. You can use #id or .class
 *                                       for example. Using JQuery
 *
 */
function saveCaretPosition(context){
    var selection = window.getSelection();
    var range = selection.getRangeAt(0);
    range.setStart(  $(context)[0], 0 );
    return range.toString().length;
}

/**
 * Restore the specified caret position in the specified context.
 *
 * Source: https://stackoverflow.com/a/38479462
 *
 * @param context String describing Jquery-style tml element selector
 * @param caretPos Integer Position of caret. MUST be returned from saveCaretPosition()
 */
function restoreCaretPosition(context, caretPos)
{
    var pos = getTextNodeAtPosition($(context)[0], caretPos);
    window.getSelection().removeAllRanges();
    var range = new Range();
    range.setStart(pos.node, pos.position);
    window.getSelection().addRange(range);
}

/**
 * Actually get the next node at the specified position.
 *
 * Source: https://stackoverflow.com/a/38479462
 */
function getTextNodeAtPosition(root, index){
    var lastNode = null;
    var treeWalker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT,function next(elem) {
        if(index > elem.textContent.length){
            index -= elem.textContent.length;
            lastNode = elem;
            return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
    });
    var c = treeWalker.nextNode();
    return {
        node: c? c: root,
        position: c? index:  0
    };
}

/*************************************\
| ************** ASYNC ************** |
\*************************************/

/**
 * Asynchronously calls /translate which will returns the processed text.
 *
 * On success: it will call the update() method.
 *
 * @param textarea Jquery-style selector Source of the text
 */
function asyncTranslate(textarea){
  var text = $(textarea).text();
  lastXhrRequest = $.ajax({
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
 * Main update function after the new text has been received
 */
function update(textarea, text, tips){
  $(ALL_TAS).removeClass('active');
  $(textarea).addClass('active');

  TIPS = tips;

  if(tips.length == 0){
    return;
  }

  var caretPos = saveCaretPosition(textarea);
  $(textarea).html(generateFormattedText(text, tips));
  restoreCaretPosition(textarea, caretPos);

  $('#tips-parent').html(generateTips(tips));

  // Update listener
  $('.tips-title').click(toggleAccordion);

  // update after T was updated
  updateScore(tips);

  // Update foundation elements (like accordion)
  $(document).foundation();
}

/*************************************\
| ********** Generate HTML ********** |
\*************************************/

function updateScore(tips){
  var ct = tips.length;
  var cg = 0;
  $(tips).each(function(k, tip){
    if(getTipPolarity(tip) == Categories.GOOD){
      cg ++;
    }
  });
  drawScore(cg / ct);
}

function drawScore(ratio)
{
  let colors = ['#f71000', '#f2d42e', '#349b38'];
  var pp = Math.round(ratio * 100);
  let rgb = lerpMultipleColor(colors, ratio);
  $('#score-container').show();
  $('#score-value').html(pp);
  $('#scorebar-filler').css({width:pp+'%', backgroundColor: rgb});
}

/**
 * Format util for the text containers
 */
function generateTextSpanBefore(index, tip, i){
  if(i == tip.start){
    return '<span id="tip-' + index + '" class="' + getPolarityText(getTipPolarity(tip)) + '">';
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
  html += generateTipsByPolarity('Améliorations possibles', 'bad', t[Categories.BAD]);
  html += generateTipsByPolarity('Conseils', 'advice', t[Categories.ADVICE]);
  html += generateTipsByPolarity('Bonnes pratiques', 'good', t[Categories.GOOD]);
  return html;
}

function generateTipsByPolarity(title, cl, tips_by_polarity){
  if(isEmpty(tips_by_polarity)){
    return '';
  }

  var count = 0;
  for(var k in tips_by_polarity){
    count += tips_by_polarity[k].length;
  }

  var html = '';
  html += '<div class="tips-container-' + cl + '">';
  html += '<div class="tips-title">';
  html += '<span class="badge">' + count + '</span>';
  html += '<span>' + title + '</span>';
  html += '</div>';
  html += '<ul class="accordion ' + cl + '" data-accordion data-multi-expand="true" data-allow-all-closed="true" style="display: none;">';
  html += Object.entries(tips_by_polarity).map(entry => generateTipsByCategory(entry)).join('');
  html += '</ul>';
  html += '</div>';

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
  html += '<div class="tip" id="tip-' + tip.index + '">' + tip.snippet + '</div>';
  return html;
}

function highlightTip(event) {
  $("span#" + event.target.id).toggleClass('active');
}

function toggleAccordion(event){
  $(this).next('.accordion').toggle();
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


  $('#tips-parent').on('mouseenter mouseleave', 'div[id^=tip-]', highlightTip);

  var key_timeout;
  $('div[id^=text-]').on('input focus', function(event) {

    if(lastXhrRequest != null){
      lastXhrRequest.abort();
    }

    clearTimeout(key_timeout);
    key_timeout = setTimeout(function(){
      asyncTranslate('#' + event.target.id);
    }, 500);
  });

});
