{% load static sekizai_tags i18n %}

class Stats{

  constructor(stat_block_selector='div.stat', url=''){
    this.stat_block = $(stat_block_selector).get(0);
    this.base_url = url
    this.debug = false
    this.stats = null
    // this.get_stats()
    this.refetch = false
    this.data_key = 'qcs_today'
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
    // self.animate_update(selector)
    $(self.stat_block).show()

  }

  check_update_view(){
    var self=this;

    if (window.location.href.search('profile') > 0){
      self.data_key = 'qcs'
      $(self.stat_block).find('.stat.stat-heading').text("{% trans 'Ngā rā katoa' %}")
    }
    
    self.update_view(
      '.stat-value.stat-total-upvotes', 
      self.stats[self.data_key]['good'])

    self.update_view(
      '.stat-value.stat-total-approvals', 
      self.stats[self.data_key]['approved'])

    self.update_view('.stat-value.stat-total-downvotes', 
      self.stats[self.data_key]['bad'])

    self.update_view('.stat-value.stat-total-total', 
      self.stats[self.data_key]['count'])
  
    self.update_view('.stat-value.stat-total-overalltotal', 
      self.stats['qcs']['count'])

  }

  logger(s){
    if (this.debug){
      console.log(s)
    }
  }

}