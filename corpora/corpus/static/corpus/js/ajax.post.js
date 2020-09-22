/*

This script sets up AJAX POST for use with Django. POST requires a CSRF token.

Requires:
1. jquery

*/


// $.xhrPool and $.ajaxSetup are the solution
$.xhrPool = [];
$.xhrPool.abortAll = function() {
    $(this).each(function(idx, jqXHR) {
        jqXHR.abort();
    });
    $.xhrPool.length = 0;
};

// Prepare a CSRF token for Ajax Post Requets
// Taken from Django Documentation
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function() {
  $.ajaxSetup({
      beforeSend: function(jqXHR, settings) {
          $.xhrPool.push(jqXHR);
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              jqXHR.setRequestHeader("X-CSRFToken", csrftoken);
          }          
      },
      complete: function(jqXHR) {
          var index = $.xhrPool.indexOf(jqXHR);
          if (index > -1) {
              $.xhrPool.splice(index, 1);
          }
      }
  });
})
