(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

require('people/js/profile.js');

},{"people/js/profile.js":2}],2:[function(require,module,exports){
'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Profile = function () {
  function Profile(pk, target_element_selector) {
    var target_alert_element_selector = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;

    _classCallCheck(this, Profile);

    this.base_url = '/api/persons/' + pk + '/';
    this.target_element = $(target_element_selector);
    this.alert_element = target_alert_element_selector == null ? null : $(target_alert_element_selector);
    this.data = null;
    this.alert = null;
    this.change_counter = 0;
    this.saving = false;
    var self = this;

    // CREATE AND REGISTER EVENT LISTENERS
    var event = document.createEvent('Event');
    event.initEvent('profile.loaded', true, true);
    this.profile_loaded_event = event;
  }

  _createClass(Profile, [{
    key: 'load',
    value: function load() {
      this.get_data();
    }
  }, {
    key: 'initialize_elements',
    value: function initialize_elements() {
      var self = this;
      $(this.target_element).find('form').on('submit', function (event) {
        event.preventDefault();
        self.save();
      });

      $(this.target_element).find('form input, form select').change(function () {
        self.change_counter += 1;
        self.save();
      });

      var elem = '<div class="alert " role="alert" style="position:absolute; right: 0;"></div>';
      this.alert = $(elem);
      $(this.alert).hide();
      if (this.alert_element == null) {
        $(this.target_element).append(this.alert);
      } else {
        $(this.alert_element).append(this.alert);
      }

      document.dispatchEvent(this.profile_loaded_event);
    }
  }, {
    key: 'get_data',
    value: function get_data() {
      var self = this;
      $.ajax({
        url: this.base_url,
        error: function error(XMLHttpRequest, textStatus, errorThrown) {
          console.error('No person exists.');
          // DO SOMETHING MEANINGFUL!
        }
      }).done(function (d) {
        self.data = d;
        self.initialize_elements();
      }).fail(function () {
        console.error('FAILED');
        // do something usefule!
      });
    }
  }, {
    key: 'save',
    value: function save() {
      var self = this;
      var demo = this.data.demographic;
      demo.age = $(this.target_element).find('#id_age').val();
      demo.sex = $(this.target_element).find('#id_sex').val();

      $.each(demo, function (key, value) {
        if (value == '') {
          delete demo[key];
        }
      });

      var tribe_list;
      tribe_list = $(this.target_element).find('#id_tribe').val();

      demo.tribe = [];
      var _iteratorNormalCompletion = true;
      var _didIteratorError = false;
      var _iteratorError = undefined;

      try {
        for (var _iterator = tribe_list[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
          var tribe_id = _step.value;

          name = $(this.target_element).find('#id_tribe option[value=' + tribe_id + ']').html();
          var json = { 'name': name, 'id': tribe_id, 'pk': tribe_id };
          demo.tribe.push(json);
        }
      } catch (err) {
        _didIteratorError = true;
        _iteratorError = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion && _iterator.return) {
            _iterator.return();
          }
        } finally {
          if (_didIteratorError) {
            throw _iteratorError;
          }
        }
      }

      this.data.demographic = demo;
      this.data.full_name = $(this.target_element).find('#id_full_name').val();

      window.setTimeout(function () {
        self.change_counter -= 1;
        if (self.change_counter <= 0) {
          if (self.change_counter < 0) {
            self.change_counter = 0;
          }

          if (self.saving == false) {
            self.put(self.data);
          } else {
            window.setTimeout(function () {
              self.change_counter += 1;
              self.save();
            }, 1500);
          }
        }
      }, 1500);
    }
  }, {
    key: 'put',
    value: function put(data) {
      var self = this;
      this.saving = true;

      $.each(data, function (key, value) {
        if (value == null) {
          delete data[key];
        }
      });

      data = JSON.stringify(data);
      $.ajax({
        type: "PUT",
        data: data,
        url: this.base_url,
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        error: function error(e) {
          console.error(e.responseText);
        }
      }).done(function () {
        self.saving = false;
        self.show_success();
      }).fail(function () {});
      return true;
    }
  }, {
    key: 'show_success',
    value: function show_success() {
      $(this.alert).addClass('alert-info').text('Profile updated').fadeIn().delay(500).fadeOut();
    }
  }, {
    key: 'post',
    value: function post(data) {
      var self = this;
      $.ajax({
        type: "POST",
        data: data,
        url: this.base_url,
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        error: function error(e) {
          console.error(e.responseText);
        }
      }).done(function () {}).fail(function () {
        console.error('POST Failed.');
      });
      return true;
    }
  }, {
    key: 'display',
    value: function display() {
      this.form_element = $(this.target_element).clone();
      $(this.target_element).empty();
      this.display_element = $("<div class='row profile profile-display-element'></div>");

      if (this.data.user != null) {
        this.display_element.append($('<div class="col-12 email" id="id_email"><span>Email:</span> <a target="_blank" href="mailto:' + this.data.user.email + '?subject=corpora.io">' + this.data.user.email + '</a></div>'));
      }
      this.display_element.append($('<div class="col-12 full_name" id="id_full_name"><span>Name:</span> ' + this.data.full_name + '</div>'));

      if (this.data.demographic != null) {
        this.display_element.append($('<div class="col-12 sex" id="id_sex"><span>Sex:</span>&nbsp;' + this.data.demographic.sex + '</div>'));
        this.display_element.append($('<div class="col-12 age" id="id_age"><span>Age:</span>&nbsp;' + this.data.demographic.age + '</div>'));
        var tribes = [];
        for (var i in this.data.demographic.tribe) {
          console.log(this.data.demographic.tribe[i]);
          tribes.push(this.data.demographic.tribe[i].name);
        }
        this.display_element.append($('<div class="col-12 tribe" id="id_tribe"><span>Tribes:</span> ' + tribes + '</div>'));
      }
      $(this.target_element).append(this.display_element);
    }
  }]);

  return Profile;
}();

},{}]},{},[1]);