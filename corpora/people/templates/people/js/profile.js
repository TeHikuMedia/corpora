
class Profile{
  constructor(pk, target_element_selector, target_alert_element_selector=null, debug=false){
    this.base_url = '/api/profile/'+pk+'/'
    this.target_element = $(target_element_selector)
    this.alert_element = (target_alert_element_selector==null) ? null : $(target_alert_element_selector);
    this.data = null
    this.old_data = null
    this.alert = null
    this.change_counter = 0
    this.saving = false
    this.debug = debug
    var self = this

    // CREATE AND REGISTER EVENT LISTENERS
    var event = document.createEvent('Event');
    event.initEvent('profile.loaded', true, true);
    this.profile_loaded_event = event;


  }

  logger(m){
    if (this.debug)
    {console.log(m)}
  }

  load(){
    this.get_data()
  }

  clone(a){
    var self = this
    var d;

    if (typeof a === 'object'){
      d = {}
    } else if (typeof a === 'list'){
      d = []
    }

    $.each(a, function(key, value){
      if (typeof value === 'object'){
        d[key] = self.clone(value)
      } else {
        d[key] = value
      }
    })
    return d
  }

  initialize_elements(){
    var self = this
    self.old_data = self.clone(self.data);
    self.logger(self.old_data)
    self.email = document.getElementById('id_email');

    try{
      self.email.addEventListener("input", function (event) {
        // Each time the user types something, we check if the
        // email field is valid.
        if (self.email.validity.valid) {
          // In case there is an error message visible, if the field
          // is valid, we remove the error message.
          // self.email.innerHTML = ""; // Reset the content of the message
          // self.email.className = "error"; // Reset the visual state of the message
          $('#id_email').removeClass('invalid')
        }
      }, false);
    }catch(e){
      self.logger(e)
    }

    $(this.target_element).find('form').on('submit', function(event){
      event.preventDefault();

      if (!self.email.validity.valid) {
        // If the field is not valid, we display a custom
        // error message.
        // error.innerHTML = "I expect an e-mail, darling!";
        // error.className = "error active";
        // And we prevent the form from being sent by canceling the event
        event.preventDefault();
      } else{
        try{self.save()}catch(e){}  
      }
      
    });

    $(this.target_element).find('form input, form select').change(function(){
      self.change_counter += 1
      self.logger('counter = '+self.change_counter)
      self.logger('Chagned')
      self.save()
    });
    

    $(this.target_element).find('.select2-selection').on('blur', function(){
      self.change_counter += 1
      self.logger('counter = '+self.change_counter)
      self.logger('Chagned')
      self.save()
    });


    var elem = '<div class="alert " role="alert"></div>'
    this.alert = $(elem)
    $(this.alert).hide()
    if (this.alert_element == null){
      $(this.target_element).append(this.alert)
    } else {
      $(this.alert_element).append(this.alert)
    }

    document.dispatchEvent(this.profile_loaded_event);

  }

  get_data(){
    var self = this;
    $.ajax({
        url: this.base_url,
        }).done(function(d){
          self.data = d;
          self.initialize_elements();
        }).fail(function(e){
          self.logger(e)
          self.logger('FAILED')
          // do something usefule!
          // document.dispatchEvent(this.profile_loaded_event);

        });
  }

  save(){
    var self = this
    var demo = this.data.demographic
    this.logger('Saving....')
    demo.age = $(this.target_element).find('#id_age').val()
    demo.gender = $(this.target_element).find('#id_gender').val()

    $.each(demo, function(key, value){
      if (value == ''){
        delete demo[key];
      }
    })

    var tribe_list;
    tribe_list = $(this.target_element).find('#id_tribe').val()

    demo.tribe = []
    for (var tribe_id of tribe_list){
      name = $(this.target_element).find('#id_tribe option[value='+tribe_id+']').html()
      var json = {'name': name, 'id': tribe_id, 'pk': tribe_id}
      demo.tribe.push(json)
    }

    this.data.demographic = demo
    this.data.full_name = $(this.target_element).find('#id_full_name').val()
    this.data.username = $(this.target_element).find('#id_username').val()

    if (this.data.user != null){
      this.data.user.email = $(this.target_element).find('#id_email').val()
    }
    
    this.data.profile_email = $(this.target_element).find('#id_email').val()

    var check_items = ['receive_weekly_updates', 'leaderboard', 'receive_daily_updates', 'receive_feedback', 'receive_emails']
    for (var i=0; i<check_items.length; i++){
      this.logger(check_items[i])
      this.data[check_items[i]] = 
        $(this.target_element).find('#id_'+check_items[i]).is(':checked');
    }

    // Set Known Languages
    // Note will need to test this works when extra forms available!
    var num_forms = $('#id_known_languages-TOTAL_FORMS').val()

    var known_languages = []
    for (var i=0; i < num_forms; i++){
      var known_language = {}
      const keys = ['id', 'accent', 'dialect', 'language', 'level_of_proficiency']      
      for (var j in keys){
        var query = '#id_known_languages-'+i+'-'+keys[j]
        self.logger(query)
        known_language[keys[j]] = $(query).val()        
      } 
      this.logger(known_language)
      known_languages.push(known_language)
    }
    this.logger(known_languages)

    this.data.known_languages = known_languages

    this.data.groups = $(this.target_element).find('#id_groups').val()
    this.logger(this.data)
    window.setTimeout(function(){
      self.change_counter -= 1
      if (self.change_counter<=0){
        if (self.change_counter<0){self.change_counter=0}

        if (self.saving == false){ 
          self.logger('Trying put...')
          self.put(self.data)  
         
          
        } else{
          window.setTimeout(function(){
            self.change_counter += 1
            self.save()
          }, 1000)
        }
      }
    }, 1000)

  } 


  put(data){
    var self = this
    this.saving = true

    $.each(data, function(key, value){
      if (value == null){
        delete data[key];
      }
    })

    data = JSON.stringify(data)
    $.ajax({
      type: "PUT",
      data: data,
      url: this.base_url,
      dataType: 'json',
      contentType:"application/json; charset=utf-8",
    }).done(function(e){
      $(".form-text-error").hide()
      $(".form-text").show()
      $('.invalid').removeClass('invalid')

      self.logger(e)
      self.saving = false
      self.show_success()
      self.old_data = self.clone(self.data);
    }).fail(function(e){
      
      self.saving = false
      $(".form-text-error").hide()
      $(".form-text").show()
      $('.invalid').removeClass('invalid')

      var errorData = e.responseJSON
      self.logger(errorData)
      $.each(errorData, function(key, value){
        if (key == 'user'){
          $.each(value, function(k, v){
            // if (k=='email'){
              // $('#id_email').addClass('invalid')
              $('#id_'+k).addClass('invalid')
              self.logger(v)
              $(".error-"+k).text(v.join(' '))
              $(".error-"+k).show()
              $(".form-text."+k).hide()
            // }
          })
        } else if (key == 'known_languages'){
          $.each(value, function(k, v){
            $.each(v, function(kk,vv){
              let kl_id = `id_${key}-${k}-${kk}`
              console.log(kl_id)
              $('#'+kl_id).addClass('invalid')
              console.log(v)
              console.log(vv)
              $(".error-"+kl_id).text(vv.join(' '))
              $(".error-"+kl_id).show()
              // $(".form-text."+kl_id).hide()
            })
          })
        } else {
          if (key=='profile_email'){key='email'}
          $('#id_'+key).addClass('invalid')
          self.logger(value)
          $(".error-"+key).text(value.join(' '))
          $(".error-"+key).show()
          $(".form-text."+key).hide()
        }
      })


    })

    return true;    
  }

  compare_dicts(a,b, append_key=''){
    var self = this
    var results = []
    var parent_key

    $.each(a, function(key, value){
      if (append_key!=''){
        parent_key = append_key+'-'+key
      } else{
        parent_key = key
      }

      if (typeof value === 'object'){
        results.push.apply(results, self.compare_dicts(value, b[key], parent_key))
      } else {

        if (typeof b === 'undefined'){
          // New object perhaps
          results.push(parent_key)
        } else if (typeof b[key] === 'undefined'){
          if (parent_key.search('group')>=0){results.push(parent_key)}
        } else if (value != b[key]){
          self.logger(value + " vs " + b[key])
          results.push(parent_key)
        } else if (typeof b === 'array'){
          self.logger('list')
          if (b[key].length != value.length){
            results.push(parent_key)
          }
        } else{
          
        }
      }
    })
    return results
  }

  show_success(){
    var self=this
    $(this.alert).addClass('alert-info').html('Profile&nbsp;updated').fadeIn().delay(500).fadeOut()
    var result;
    result = this.compare_dicts(this.data, this.old_data)
    self.logger( result )

    $.each(result, function(key, value){
      if (value=='profile_email'){value='email'}
      var objs = $('#id_'+value)
      var selector;
      if (objs.length==0){
        var parts = value.split('-')
        for (var i=0; i< parts.length; i++){
            objs = $('#id_'+parts[i])
            if (objs.length>0){
              selector = objs
            }
        }
      } else{
        selector = objs
      }

      if (typeof selector !== 'undefined'){
        selector.addClass('valid')
        window.setTimeout(function(){
          selector.removeClass('valid')
        }, 2000)        
      }



    })

  }

  post(data){
    var self = this
    $.ajax({
      type: "POST",
      data: data,
      url: this.base_url,
      dataType: 'json',
      contentType:"application/json; charset=utf-8",
    }).done(function(){
    }).fail(function(){
      self.logger('POST Failed.')
    })
    return true;    
  }

  display(){
    var self = this;
    this.form_element = $(this.target_element).clone()
    $(this.target_element).empty()
    this.display_element = $("<div class='row profile profile-display-element'></div>")

    if (this.data.user != null){
      this.display_element.append($('<div class="col-12 email" id="id_email"><span>Email:</span> <a target="_blank" href="mailto:'
      +this.data.user.email+'?subject=corpora.io">'+this.data.user.email+'</a></div>'))
    }
    this.display_element.append($('<div class="col-12 full_name" id="id_full_name"><span>Name:</span> '+this.data.full_name+'</div>'))

    if (this.data.demographic != null){ 
      this.display_element.append($('<div class="col-12 sex" id="id_sex"><span>Sex:</span>&nbsp;'+this.data.demographic.sex+'</div>'))
      this.display_element.append($('<div class="col-12 age" id="id_age"><span>Age:</span>&nbsp;'+this.data.demographic.age+'</div>'))
      var tribes = []
      for (var i in this.data.demographic.tribe){
        self.logger(this.data.demographic.tribe[i])
        tribes.push(this.data.demographic.tribe[i].name)
      }
      this.display_element.append($('<div class="col-12 tribe" id="id_tribe"><span>Tribes:</span> '+tribes+'</div>'))
    }

    if (this.data.known_languages != null){ 
      for (var i = 0; i < this.data.known_languages.length; i++){
        var language_obj = this.data.known_languages[i]
        var language = null;
        if (typeof listen !== 'undefined'){
          language = listen.sentence.language
        } else if (language_obj.active) {
          language = language_obj.language
        }

        if (language_obj.language == language){
          this.display_element.append($('<div class="col-12 dialect" id="id_language"><span>Language:</span>&nbsp;'+language_obj.language+'</div>'))
          this.display_element.append($('<div class="col-12 dialect" id="id_dialect"><span>Dialect:</span>&nbsp;'+language_obj.dialect+'</div>'))
          this.display_element.append($('<div class="col-12 proficiency" id="id_proficiency"><span>Proficiency:</span>&nbsp;'+language_obj.level_of_proficiency+'</div>'))  
        }

      }
    }




    $(this.target_element).append(this.display_element)
  }


}
