class AudioFileTranscriptionEditor{

  constructor(){
    this.aft_list = []
    this.currentRequest = null
    this.isMobile = false; //initiate as false

    // device detection
    if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) 
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) { 
      this.isMobile = true;
    }


    var self=this
    $('[x-data-model="audio_file_transcription"][x-data-action="edit"]').each(function(index,element){
      $(element).on('click', function(event){
        event.stopPropagation();
        if (event.delegateTarget == event.target){
          window.location = event.delegateTarget.attributes['x-data-url'].value    
        }
      })
    })

    $('[x-data-model="audio_file_transcription"][x-data-action="download"]').each(function(index,element){
      $(element).on('click', function(event){
        // event.stopPropagation();
        self.download(event.delegateTarget)
      })
    })    

    // Set status for files being transcribed
    $('[x-data-model="audio_file_transcription"][x-data-field="transcription"]').each(function(index,element){
      // if ($(element).attr('x-data-value') == ''){
      self.get_status(element)
      // }
    }) 

    $('[x-data-model="audio_file_transcription"][x-data-field]').each(function(index,element){
      $(element).on('blur', function(event){
        event.stopPropagation();
        self.save(event.target)
      })
    })

    $('a[x-data-model="audio_file_transcription"][x-data-action="delete"]').each(function(index,element){
      $(element).on('click', function(event){
        event.stopPropagation();
        event.preventDefault();
        var id = element.attributes['x-data-id'].value
        var name = $(`[x-data-model="audio_file_transcription"][x-data-id="${id}"][x-data-field="name"]`).get(0).attributes['x-data-value'].value

        self.create_modal(
          'Confirm Delete',
          `Are you sure you want to delete <b>${ name }</b>? This cannot be undone.`,
          'Delete',
          function(){
            self.delete(event.delegateTarget)
            return true;
          })
      })
    })

    $('a[x-data-model="audio_file_transcription"][x-data-action="create"]').each(function(index,element){
      $(element).on('click', function(event){
        event.stopPropagation();
        event.preventDefault();


        var form =`
        <form id='file-upload' action="/api/transcription/" method="post" enctype="multipart/form-data">
          <input type="file" id="audio_file" name="audio_file" />
          <input type="hidden" name="uploaded_by" value="{{person.pk}}">
        </form>`


        
        self.create_modal(
          'Upload Audio',
          form,
          'Upload',
          function(){
            var form = $('#file-upload')[0];
            var f = document.getElementById('audio_file').files[0]
            var fd = new FormData($("#file-upload")[0]);

            if (f == undefined){
              // Need to select a file
              return false;
            } else{
              fd.append('name', f.name);
              self.create(fd)
              return true;
            }
          })
      })
    })

  }

  create(form_data){
    var self=this;
    var progress_bar = `
        <div class="progress" style="margin-top: 15px;">
          <div class="progress-bar-upload progress-bar progress-bar-striped progress-bar-animated bg-danger" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%"></div>
        </div>
`
    $('.modal-body').append(progress_bar)

    this.currentRequest = $.ajax({
        url: '/api/transcription/',
        type: 'POST',
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        xhr: function() {
          var xhr = new window.XMLHttpRequest();
          xhr.upload.addEventListener("progress", function(evt) {
            if (evt.lengthComputable) {
                var percentComplete = parseInt(evt.loaded / evt.total * 100);
                //Do something with upload progress here
                console.log(percentComplete)
                $('.progress-bar-upload').attr({
                  'aria-valuenow': percentComplete,
                  style: "width: "+percentComplete+"%",});

                // $(".modal-title").html('Uploading... '+percentComplete+"%")
                
            }
          }, false);
          return xhr
        },         
    }).done(function(){
      self.currentRequest=null
      window.setTimeout(function(){window.location = '/transcriptions/'}, 1000)
    });
  
  }

  save(element){
    var self=this;
    var formData = new FormData();
    var id = element.attributes['x-data-id'].value
    var field = element.attributes['x-data-field'].value
    var url = '/api/transcription/'+id+'/'
    formData.append(field, $.trim($(element).text()))
    formData.enctype = "multipart/form-data"
    $.ajax({
      url: url,
      data: formData,
      type: "PUT",
      cache: false,
      contentType: false,
      processData: false,
    }).done(function(){
      self.currentRequest=null
    })
  }

  delete(element){
    var id = element.attributes['x-data-id'].value
    var url = '/api/transcription/'+id+'/'
    this.currentRequest = $.ajax({
      url: url,
      type: "DELETE",     
    }).done(function(){
      self.currentRequest=null
      location.reload()
    })    
  }

  get_status(element){
    var self = this
    var id = element.attributes['x-data-id'].value
    var url = '/api/transcription/'+id+'/'
    
    // We don't use this.current request here

    $.ajax({
      url: url,
      type: "GET",     
    }).done(function(response){
      var percentComplete = (response.status.percent == 0) ? 1 : response.status.percent
      $(element).empty()

      if (percentComplete<100){
        var progress_bar = `
          <div class="progress" style="margin-top: 15px;">
            <div class="progress-bar-${$(element).attr('x-data-id')} progress-bar progress-bar-striped progress-bar-animated bg-danger"
            role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%"></div>
          </div>`

        
        $(element).append(progress_bar)
        $(`.progress-bar-${$(element).attr('x-data-id')}`).attr({
                    'aria-valuenow': percentComplete,
                    style: "width: "+percentComplete+"%",});

        window.setTimeout(function(){
          self.get_status(element)
        }, 5000)

      } else if (percentComplete == 100){
        $(element).append(`<em>${response.transcription.slice(0,64)}</em>`)
      }

    }).fail(function(error){
      console.log(error)
      window.setTimeout(function(){
          self.get_status(element)
        }, 10000)
    })    
  }

  download(element){
    var format;
    var id = element.attributes['x-data-id'].value
    try{
      format = element.attributes['x-data-format'].value
    } catch { format = 'txt'}
    var link = document.createElement("a");
    link.download = element.attributes['x-data-file-name'].value
    link.href = '/api/transcription/'+id+'.'+format;
    if (this.isMobile){
      window.open(link.href, '_blank')
    } else{
      link.click()
    }
  }

  add_object(){




  }

  create_modal(heading, message, action, method){
    // Destroy all other models before making a new one.
    // $('.temporary-modal .modal').each(function(index, element){
    //   element.modal('dispose')
    // })
    $('.temporary-modal').remove();
    var self = this;
    var element = $('<div class="temporary-modal"></div>')
    var button_class = 'danger'
    if (action.toLowerCase().search('delete')>=0){
      button_class = 'danger'
    }


    

    var template = `
<div class="modal fade bd-example-modal-sm" tabindex="-1" role="dialog" aria-labelledby="confirmAction" aria-hidden="true">
  <div class="modal-dialog ">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">${heading}</h5>

      </div>
      <div class="modal-body">
        <div id='modal-message'>${message}</div>
      </div>      
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal" >Cancel</button>
        <button type="button" class="btn btn-${button_class}" x-data-confirm="true">${action}</button>
      </div>
    </div>
  </div>
</div>
`

    $(element).append(template);
    // Add the element to the dom
    $(document.body).append(element);

    // $(element).find('#modal-message').append($(message))

    // Create the modal
    $(element).find('.modal').modal({'backdrop': 'static'})

    $(element).find('[x-data-confirm="true"]').each(function(index, elm){
      var spinner = "<i class='fas fa-circle-notch fa-spin'></i>";
      $(elm).on('click', function(){
        if (self.currentRequest == null){
          var result = method();
          if (result){
            $(elm).text("")
            $(elm).append(spinner)
          }
        }
      })
    })

    $(element).find('[data-dismiss="modal"]').each(function(index, elm){
      $(elm).on('click', function(){
        self.currentRequest.abort()
        self.currentRequest = null
      })
    })    

  }





}