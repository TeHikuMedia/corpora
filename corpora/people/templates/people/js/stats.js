{% load static sekizai_tags i18n %}

class Stats{

  constructor(stat_block_selector='.stat', url=''){
    this.stat_block = $(stat_block_selector).get(0);
    this.base_url = url
    this.debug = false
    this.stats = null
    // this.get_stats()
    this.refetch = false
    this.data_key = 'recordings_today'
    // var event = document.createEvent('Event');
    // event.initEvent('sentence.ready', true, true);
    // this.sentence_block_ready_event = event;
  }

  get_stats(){
    var self = this;
    self.logger('Fetching stats')
    $.ajax({
        url: this.base_url
        }).done(function(d){
          self.stats = d
          self.logger(d)
          self.check_update_view();
    })
  }

  animate_update(selector){
    var self = this
    window.setTimeout(function(){
      $(self.stat_block).find(selector)
      .addClass('stat-value-animate-up')
      .removeClass('stat-value-animate-down')
    }, 100);
    
    window.setTimeout(function(){
      $(self.stat_block).find(selector)
      .addClass('stat-value-animate-down')
      .removeClass('stat-value-animate-up')
    }, 200);

  }

  update_view(selector, value){
    var self = this

    if (selector.indexOf('seconds')>0){
      if (value>60){
        value = (value/60).toFixed(1)
        $(self.stat_block).find('.stat.stat-dimension.stat-total-seconds').html("<br>"+
          self.stats[self.data_key]['dimension_string'])
      }
    }
    $(self.stat_block).find(selector).text(value)
    $(self.stat_block).find(selector).attr('data-value',value)
    self.animate_update(selector)
    $(self.stat_block).show()

  }

  check_update_view(){
    var self=this;
    var old_num_recordings = undefined
    var old_duration = undefined

    if (window.location.href.search('profile') > 0){
      self.data_key = 'recordings'
      $(self.stat_block).find('.stat.stat-heading').text("{% trans 'Ngā rā katoa' %}")

    }

    old_num_recordings = parseInt($(self.stat_block).find('.stat-value.stat-total-recordings').attr('data-value'))
    old_duration = parseInt($(self.stat_block).find('.stat-value.stat-total-seconds').attr('data-value'))

    var recordings = self.stats[self.data_key]['total']
    var duration = self.stats[self.data_key]['total_seconds']

    self.logger(old_num_recordings)
    if (isNaN(old_num_recordings)){
      self.logger('updating view')
      self.update_view('.stat-value.stat-total-seconds', duration)
      self.update_view('.stat-value.stat-total-recordings', recordings)
    }

    else if (old_num_recordings != recordings){
      self.logger('Checking duration change')

      self.update_view('.stat-value.stat-total-recordings', recordings)

      // CHeck that duration also changed, if not, show a loading
      // And fet utnil it updates
      self.logger(old_duration)
      if (old_duration != duration){
        self.update_view('.stat-value.stat-total-seconds', duration)
      } else{
        window.setTimeout(function(){
          self.get_stats()
        }, 1000)
      }

      self.refetch = true
    } else if (self.refetch){

      if (old_duration != duration){
        self.update_view('.stat-value.stat-total-seconds', duration)
        self.refetch = false
      } else{
        window.setTimeout(function(){
          self.get_stats()
        }, 2000)
      }      
    }
  }

  logger(s){
    if (this.debug){
      console.log(s)
    }
  }

}