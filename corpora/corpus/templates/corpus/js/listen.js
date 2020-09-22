class Listen{
  constructor(person_pk, target_element_selector, content_type, admin=false, editor=false, user_id=null, debug=false){
    var self = this;
    this.debug = debug
    this.sentence_block = $(target_element_selector)
    this.admin = admin
    this.editor = editor
    this.user_id = user_id
    this.objects = null
    this.recording = null
    this.sentence = null
    this.fetching = false
    this.showing_next_recording = false
    if(admin){
      this.base_url = '/api/recordings/'
      this.base_recording_url = '/api/recordings/'
      this.url_filter_query = '?sort_by=listen'
    } else{
      this.base_url = '/api/listen/'
      this.base_recording_url = '/api/listen/'
      this.url_filter_query = '?sort_by=random'
    }
    
    this.base_quality_url = '/api/qualitycontrol/'
    this.next_url = null
    this.quality_control = {}
    this.quality_control.person = person_pk
    this.error_loop = 0
    this.audio = document.getElementById('play-audio');
    // this.quality_control.content_type = content_type
    $(this.sentence_block).fadeOut(0)

    
    $(self.sentence_block).find('.approve').off().on('click', function(e){
      if (!$(e.currentTarget).hasClass('disabled')){
        $(self.sentence_block).find('.actions a').addClass('disabled')
        $(self.sentence_block).find('.actions a.help').removeClass('disabled')
        self.approve();
      }
    })

    $(self.sentence_block).find('.good').off().on('click', function(e){
      if (!$(e.currentTarget).hasClass('disabled')){
        $(self.sentence_block).find('.actions a').addClass('disabled')
        $(self.sentence_block).find('.actions a.help').removeClass('disabled')
        self.up_vote();
      }
    })   

    $(self.sentence_block).find('.bad').off().on('click', function(e){
      if (!$(e.currentTarget).hasClass('disabled')){
        $(self.sentence_block).find('.actions a').addClass('disabled')
        $(self.sentence_block).find('.actions a.help').removeClass('disabled')
        self.down_vote();
      }
    })

    $(self.sentence_block).find('.bad').off().on('click', function(e){
      if (!$(e.currentTarget).hasClass('disabled')){
        $(self.sentence_block).find('.actions a').addClass('disabled')
        $(self.sentence_block).find('.actions a.help').removeClass('disabled')
        self.down_vote();
      }
    })

    $(self.sentence_block).find('.star').off().on('click', function(e){
      if (!$(e.currentTarget).hasClass('disabled')){
        self.star_rating(e.currentTarget);
      }
    })

    $(self.sentence_block).find('.follow-up, .noise, .delete').off().on('click', function(e){
      if (!$(e.currentTarget).hasClass('disabled')){
        if (!$(e.currentTarget).hasClass('checked')){
          $(e.currentTarget).addClass('checked')
        } else{
          $(e.currentTarget).removeClass('checked')
        }
        self.toggle_boolean(e.currentTarget);
      }
    })

    $(self.sentence_block).find('.next').unbind().on('click', function(e){
      if (!$(e.currentTarget).hasClass('disabled')){
        $(self.sentence_block).find('.actions a').addClass('disabled')
        $(self.sentence_block).find('.actions a.help').removeClass('disabled')
        self.audio.pause()
        // self.audio.src=null
        self.next();
      }
    })  


    // CREATE AND REGISTER EVENT LISTENERS
    var event = document.createEvent('Event');
    event.initEvent('listen.recording.loaded', true, true);
    this.recording_loaded_event = event;

  }

  show_loading(){
    $('.circle-button-container a').hide();
    $('.circle-button-container a.loading').show()   
  }

  hide_loading(){
    $('.circle-button-container a').hide();
  }

  get_recordings(){
    var self = this;
    self.logger('Fetching more recordings')
    self.show_loading()
    if (self.fetching){ return; }
    self.fetching = true;
    $.ajax({
      url: ( (this.next_url==null) ? this.base_url + this.url_filter_query : this.next_url),
      error: function(XMLHttpRequest, textStatus, errorThrown){
        self.logger('ERROR fetching recordings')
        self.fetching = false;
      }
      }).done(function(d){
        self.objects = d.results
        self.next_url = d.next

        if (self.objects.length == 0 || self.error_loop>3){
          self.logger('No more recordings')
          self.all_done()
        }
        else{
          self.logger('Got recordings')
          self.logger(self.objects[0])
          self.next()
        }
        self.fetching = false;
      }).fail(function(){
        self.logger('Failed to fetch recordings, will try again...')
        window.setTimeout( function(){
          self.next_url=null
          self.get_recordings()
          self.hide_loading()
        }, 1500 )
        self.fetching = false;
      });
  }

  reload(){
    var self = this
    $.ajax({
        url: this.base_recording_url+this.recording.id+'/'
        }).done(function(d){
          self.logger('Reloaded')
          self.logger(d)
          self.recording.quality_control = d.quality_control
          self.recording = d
          self.sentence = d.sentence
          self.objects.push(d)
          self.next()
    })    
  }

  next(){
    var self = this
    this.logger('Next')
    if (this.objects == null || this.objects.length==0){
      this.get_recordings()
    } else{
      this.recording = this.objects.shift()
      this.sentence = this.recording.sentence

      this.logger(this.recording)
      this.logger(this.recording.id)
      if (this.recording.sentence_text == '' || this.recording.sentence_text==null){
        if (this.sentence==null){
          this.recording.sentence_text = 'These arent teh droid your looking for'
          this.logger('error')
          this.error_loop+=1
          // this.show_next_recording()
          this.next()
        } else { this.recording.sentence_text = this.sentence.text }
      }

      if (this.sentence==null && this.recording.sentence_text.length>0){
        this.sentence = {}
        this.sentence.text=this.recording.sentence_text
      }

      // Untoggle checks, and also reset their values to default which should be false
      $('.toggle-after-playback').removeClass('checked')
      $('.toggle-after-playback').find('[data-icon=star]').attr('data-prefix', 'far');
      self.logger('RESETTING QUALITY CONTROL\n')
      $('.toggle-after-playback').each(function(i,o){

        if (self.quality_control[$(o).attr('data-key')] != undefined){
          self.logger('Need to reset ' + $(o).attr('data-key'))

          if ($(o).hasClass('star') || $(o).hasClass('good') || $(o).hasClass('bad')){
            self.quality_control[$(o).attr('data-key')] = 0
          
          } else if ($(o).hasClass('approve')){
            self.logger('RESET Approve')
            self.quality_control[$(o).attr('data-key')] = false
            self.quality_control.approved_by = null
          
          } else {
            self.quality_control[$(o).attr('data-key')] = false
          }
        
        } else {
          self.logger('NOT RESETTING ' + $(o).attr('data-key'))
        }
      })

      this.show_next_recording()
    }


  }

  all_done(){
    $(this.sentence_block).text("All done.")
    $(this.sentence_block).fadeIn('disabled')
  }

  show_next_recording(){
    var self = this;

    self.logger('Show next recording')
    self.show_loading();

    if (self.showing_next_recording){ return ;}

    if (self.sentence){
      self.showing_next_recording = true

      $(self.sentence_block).removeClass('disabled')
      $(self.sentence_block).find('.sentence .text-area').remove()


      var display_text = self.recording.sentence_text

      if (self.editor){
        var input_elm = $('<textarea id="editText" class="text-area" type="textarea" name="text" rows="4">')
        $(input_elm).val(display_text);
        $(this.sentence_block).find('.sentence').append(input_elm)
        $(this.sentence_block).fadeIn('fast');        
        $(this.sentence_block).find('.sentence').textfill({
          maxFontPixels: 40,
          innerTag: 'textarea',
          success: function(){
            var space = 
              parseFloat($(this.sentence_block).find('.sentence').parent().css('line-height')) /
              parseFloat($(this.sentence_block).find('.sentence').parent().css('font-size'))
              $(this.sentence_block).find('.sentence').css('line-height', space+'px')
          }
        })

      } else {

        var input_elm = $('<span class="text-area"></span>')
        $(input_elm).text(display_text);
        $(this.sentence_block).find('.sentence').append(input_elm)
        $(this.sentence_block).fadeIn('fast');        
        $(this.sentence_block).find('.sentence').textfill({
          maxFontPixels: 40,
          success: function(){
            var space = 
              parseFloat($(this.sentence_block).find('.sentence').parent().css('line-height')) /
              parseFloat($(this.sentence_block).find('.sentence').parent().css('font-size'))
              $(this.sentence_block).find('.sentence').css('line-height', space+'px')
          }
        })

      }
      
      // Load extra info if available
      $(this.sentence_block).find('.extra-info').empty()
      if (self.recording.transcription != null){
        var transcription_elm = $(`<div id='transcription'>Transcription: ${self.recording.transcription}</div>`)
        $(this.sentence_block).find('.extra-info').append(transcription_elm)
      }
      if (self.recording.word_error_rate != null){
        var wer_elm = $(`<div id='wer'>Word Error Rate: ${self.recording.word_error_rate.toFixed(2)}</div>`)
        $(this.sentence_block).find('.extra-info').append(wer_elm)
      }

      // $('#play-button').show();

      $.ajax({
        type: "GET",
        url: this.base_recording_url+this.recording.id+'/',
        dataType: 'json',
        error: function(XMLHttpRequest, textStatus, errorThrown){
          self.logger(textStatus.responseText)
          self.logger(XMLHttpRequest)
          self.logger(errorThrown)
          self.showing_next_recording = false
        }
      }).done(function(){

        $(self.sentence_block).find('.next, .auto-play').removeClass('disabled')
        self.hide_loading()
        self.audio.src = self.recording.audio_file_url
        self.audio.oncanplay=function(){

          document.dispatchEvent(self.recording_loaded_event);
        }
        self.audio.load()
        self.showing_next_recording = false
      }).fail(function(){
        console.error('FAILED TO GET RECORDING FILE')
        window.setTimeout(function(){
          self.next()
        }, 1500)
        self.showing_next_recording = false
      })


      $(input_elm).on('change', function(){
        self.edit_sentence()
      })

      $(input_elm).on('keyup', function(event){
        self.check_sentence_changed(event)
      })

      $(self.audio).bind('error', function(){
        window.setTimeout(function(){
          self.next()
        }, 1500);
        self.showing_next_recording = false
      })

      $(self.audio).bind('emptied', function(){
        self.logger('audio source emptied')
        self.showing_next_recording = false
      });
    }
  }

  check_sentence_changed(event){
    if ($(event.currentTarget).val() != this.sentence.text){
      this.edit_sentence()
    }
  }

  edit_sentence(){
    var self = this
    $(self.sentence_block).find('.approve, .good, .bad').addClass('disabled')
    $(self.sentence_block).find('.save').removeClass('off').removeClass('disabled')
    $(self.sentence_block).find('.save').off().on('click', function(e){
        $(e.currentTarget).addClass('disabled').off()
        self.save_sentence($(self.sentence_block).find('.text-area').val());
    })     
  }

  post_qc(data){
    var self = this
    self.show_loading()
    this.quality_control.recording = this.recording.id
    self.logger(this.quality_control)
    self.logger(this.quality_control.recording)
    $.ajax({
      type: "POST",
      data: this.quality_control,
      url: this.base_quality_url,
      dataType: 'json',
      error: function(XMLHttpRequest, textStatus, errorThrown){
        self.logger(XMLHttpRequest.status)
        self.logger(XMLHttpRequest.responseText)
        self.hide_loading()
      }
    }).done(function(){
      self.next();
    }).fail(function(){
      self.logger('Failed.')
      // self.hide_loading()
      self.next()
    })
    return true;    
  }

  put_qc(data){
    var self = this
    self.show_loading()
    $.ajax({
      type: "PUT",
      data: data,
      url: this.base_quality_url+this.quality_control_id+'/',
      dataType: 'json',
      error: function(e){
        self.logger(e.responseText)
        self.hide_loading()
      }
    }).done(function(){
      self.next();
    }).fail(function(){
      self.logger('Failed.')
      self.next()
    })
    return true;    
  }

  save_sentence(text){
    var self=this
    this.recording.sentence_text = text
    self.show_loading()
    var data = {
      id: this.recording.id,
      sentence_text: text
    }

    $.ajax({
      type: "PUT",
      data: data,
      url: this.base_recording_url+this.recording.id+'/',
      dataType: 'json',
      error: function(XMLHttpRequest, textStatus, errorThrown){
        self.logger(textStatus.responseText)
        self.logger(XMLHttpRequest)
        self.logger(errorThrown)
        self.hide_loading()
      }
    }).done(function(){
      self.logger('Saved')
      self.reload();
      self.hide_loading()
    }).fail(function(){
      self.logger('Failed.')
      self.next()
    })
  }

  post_put(){
    var self = this
    var method = 'POST'
    this.quality_control.recording = this.recording.id
    this.audio.pause()
    if (this.recording.quality_control){
      for (let qc of this.recording.quality_control){
        if (qc.person == this.quality_control.person){
          self.logger('Found matching qc ')
          this.quality_control_id = qc.id
          this.quality_control.bad += qc.bad
          this.quality_control.good += qc.good
          method = 'PUT'
        } else{
          
        }
      }
    }

    if (method=='POST'){
      this.post_qc(this.quality_control)
    } else {
      this.put_qc(this.quality_control)
    }

  }

  approve(){
    this.quality_control.approved = true;
    this.quality_control.good = 0
    this.quality_control.bad = 0    
    this.quality_control.approved_by = this.user_id;
    this.logger(this.quality_control);
    this.post_put();
  }
  up_vote(){
    this.quality_control.good = 1
    this.quality_control.bad = 0
    // this.quality_control.approved = false;
    this.logger(this.quality_control);
    this.post_put();
  }

  down_vote(){
    this.quality_control.bad = 1
    this.quality_control.good = 0
    // this.quality_control.approved = false;
    this.logger(this.quality_control);
    this.post_put();
  }

  star_rating(object){
    var self=this
    var parent = $(object).parent()
    var children = $(parent).children()
    var index = $(object).index()
    var clearall = false
    self.quality_control['star'] = 0

    try {
      if (!$(children[index+1]).hasClass('checked') && $(object).hasClass('checked')){
        clearall = true
      }
    } catch(e){ clearall=true }

    if (clearall){
      $(parent).children().each(function(i,e){
        $(children[i]).removeClass('checked') 
        $(children[i]).find('[data-icon=star]').attr('data-prefix', 'far');
      })
    } else if ($(object).hasClass('checked')){
      for (var i=children.length; i >= 0; i--){
        if (i <= $(object).index()){
          $(children[i]).addClass('checked')
          $(children[i]).find('[data-icon=star]').attr('data-prefix', 'fas');
          self.quality_control['star'] += 1
        } else {
          $(children[i]).removeClass('checked') 
          $(children[i]).find('[data-icon=star]').attr('data-prefix', 'far');
        }
      }

    } else {
      // Check all stars up to it.
      $(parent).children().each(function(i,e){
        if (i <= $(object).index()){ 
          $(children[i]).addClass('checked')
          $(children[i]).find('[data-icon=star]').attr('data-prefix', 'fas');
          self.quality_control['star'] += 1
        } else {
          $(children[i]).removeClass('checked') 
          $(children[i]).find('[data-icon=star]').attr('data-prefix', 'far');
        }
      })
    }


    this.logger(self.quality_control['star'])

  }

  toggle_boolean(button_object){
    this.quality_control[$(button_object).attr('data-key')] = $(button_object).hasClass('checked')
    
    if ($(button_object).hasClass('star')){
      if ($(button_object).hasClass('checked')){
        this.quality_control[$(button_object).attr('data-key')] = 1
      } else {
        this.quality_control[$(button_object).attr('data-key')] = 0
      }
    }

    if ($(button_object).hasClass('delete')){
      if ($(button_object).hasClass('checked')){
        $(this.sentence_block).find('.actions a').addClass('disabled')
        this.quality_control.bad = 1
        this.post_put()
      }
    }    

    this.logger(this.quality_control);
  }

  logger(s){
    if (this.debug){
      console.log(s)
    }
  }

}