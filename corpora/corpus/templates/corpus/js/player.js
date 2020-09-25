class Player {
  constructor(target_element_selector, audio_element_id='play-audio', debug=false){
    var self = this;    
    this.actions_element = $(target_element_selector).get(0)
    this.audio = document.getElementById(audio_element_id);

    this.stop_button = document.getElementById('stop-button')
    this.play_button = document.getElementById('play-button')
    this.loading_button = document.getElementById('loading-button')
    this.record_button = document.getElementById('record-button')

    this.debug = debug;

    $(this.play_button).on('mousedown', function(){
      $('.foreground-circle.play').removeClass('unclicked-circle').addClass('clicked-circle');
      $(self.play_button ).on('blur', function(){
        $('.foreground-circle.play').addClass('unclicked-circle').removeClass('clicked-circle');
      });

    });
    
    $(this.play_button).click(function(){
      self.audio.play();
    });    

    $(this.stop_button).click(function(){
      self.audio.pause();
    });  

    // When audio is done playing back, revert button to initial state
    $(this.audio).bind('ended', function(){
      $('.foreground-circle.play').removeClass('clicked-circle').addClass('unclicked-circle');
    });

    // Get the local storage stting for autoplay.
    try{
      var autoplay = window.localStorage.getItem('play:autoplay')
      console.log(autoplay)
      if (autoplay){
        if (autoplay=='true'){
          $('a.auto-play').addClass('auto-play-on')
          $('a.auto-play').removeClass('auto-play-off')
        }
      }
    } catch(e){

    }

    $('a.auto-play').click(function(event){
      var obj = event.currentTarget
      self.logger('auto play clicked')
      if ($(obj).hasClass('auto-play-off')){
        $(obj).removeClass('auto-play-off')
        $(obj).addClass('auto-play-on')

        try{
          window.localStorage.setItem('play:autoplay', true)
        } catch(e){
          console.log('Could not set play:autoplay')
        }

        self.audio.autoplay=true;

      } else {
        self.audio.autoplay=false;
        $(obj).removeClass('auto-play-on')
        $(obj).addClass('auto-play-off')
        try{
          window.localStorage.setItem('play:autoplay', false)
        } catch(e){
          console.log('Could not set play:autoplay')
        }
      }

    })

    $(this.audio).bind('loadstart', function(){
      self.logger('audio load started')
      self.hide_all_buttons();
      $(self.loading_button).show()
      self.logger('loading button shown')
    });

    $(this.audio).bind('emptied', function(){
      self.logger('audio source emptied')
      self.hide_all_buttons();
    });

    $(this.audio).bind('loadeddata', function(e){
      self.logger('audio loadeddata or canplay '+e)
      self.hide_all_buttons();
      
      if ($('a.auto-play').hasClass('auto-play-on')){
        self.audio.play().then().catch(function(){
          // self.audio.pause()
          self.hide_all_buttons();
          $('.foreground-circle.play').removeClass('clicked-circle').addClass('unclicked-circle');
          $(self.play_button).show()

        });

      } else if (self.audio.src != null){
        $(self.play_button).show()
        self.logger('show play button')
      }

    });

    $(this.audio).bind('stalled', function(){
      self.logger('audio stalled')
    });

    $(this.audio).bind('suspend', function(){
      self.logger('audio suspended')
    });    

    $(this.audio).bind('play', function(){
      self.logger('audio played')
      self.hide_all_buttons();
      $(self.loading_button).show()
      $('.foreground-circle.loading').addClass('clicked-circle').removeClass('unclicked-circle').show();  
    });

    $(this.audio).bind('playing', function(){
      self.logger('audio playing')
      self.logger(self.audio.src)
      self.hide_all_buttons();
      $('.foreground-circle.loading').removeClass('clicked-circle').addClass('unclicked-circle')
      $('.foreground-circle.stop').addClass('clicked-circle').removeClass('unclicked-circle')
      $(self.stop_button).show()
    });

    $(this.audio).bind('pause', function(){
      self.logger('audio paused')
      self.hide_all_buttons();
      $('.foreground-circle.play').removeClass('clicked-circle').addClass('unclicked-circle');
      $(self.play_button).show()
      self.audio.currentTime = 0;
    });

    $(this.audio).bind('ended', function(){
      self.logger('audio ended')
      self.hide_all_buttons();
      $('.foreground-circle.play').removeClass('clicked-circle').addClass('unclicked-circle');
      $(self.play_button).show()
      $(self.actions_element).find('.toggle-after-playback').removeClass('disabled')
    });



  }

  hide_all_buttons(){
    $(this.play_button).hide()
    $(this.stop_button).hide()
    $(this.loading_button).hide()
    $(this.record_button).hide()
    this.logger('All buttons hidden')
  }

  logger(s){
    if (this.debug){
      console.log(s)
    }
  }

}