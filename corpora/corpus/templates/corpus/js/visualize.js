


class Visualize{

  constructor(canvas_id, sourceNode, audioContext){
    var self = this
    this.canvas = document.getElementById(canvas_id)
    this.canvasContext = this.canvas.getContext("2d")
    this.loop = false
    this.sourceNode = sourceNode
    this.audioContext = audioContext
    this.analyser = audioContext.createAnalyser();
    this.analyser.fftSize = 32;


    this.sourceNode.connect(this.analyser);
    
    this.bufferLength = this.analyser.frequencyBinCount;
    this.dataArray = new Uint8Array(this.analyser.fftSize);

  }

  stop(){
    this.loop = false
    var self = this
    window.setTimeout(function(){self.clearFrame()}, 200)
  }

  start(){
    this.canvas.width = this.canvas.clientWidth;
    this.canvas.height = this.canvas.clientHeight;    
    this.WIDTH = this.canvas.clientWidth;
    this.HEIGHT = this.canvas.clientHeight;    
    this.loop = true
    this.renderFrame();
  }

  renderFrame() {
    var self = this
    if (self.loop){
      
      // if (navigator.userAgent.match(/(Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini)/) && Math.random()*100<0) {
  
      //   window.setTimeout(
      //     function(){
      //       window.requestAnimationFrame(function(){self.renderFrame()});
      //     }, 500)

      // } else{

        window.requestAnimationFrame(function(){self.renderFrame()});
        self.analyser.getByteFrequencyData(self.dataArray);
        // self.canvasContext.clearRect(0, 0, self.WIDTH, self.HEIGHT);
        self.canvasContext.fillStyle = "#333";
        self.canvasContext.fillRect(0, 0, self.WIDTH, self.HEIGHT);

        var barWidth = parseInt((self.WIDTH / self.bufferLength))
        var barHeight = 0
        var x = 0;

        for (var i = 0; i < self.bufferLength/2; i++) {
          barHeight = parseInt(self.dataArray[i]/255*self.HEIGHT*.9);
          
          var h = 345
          var s = parseInt(73 * ( self.HEIGHT/barHeight * .5) )
          var l = parseInt(90 * ( barHeight/self.HEIGHT))
          
          self.canvasContext.fillStyle = "hsl(" + h + "," + s + "%," + l + "%)";
          self.canvasContext.fillRect(2*x+1, self.HEIGHT - barHeight, 2*barWidth-2, barHeight);

          x += barWidth;

          // console.log(parseInt(barHeight), self.HEIGHT)

        // }
      }
      
    } else {
      return;
    }
  }

  clearFrame(){
    var self = this
    self.canvasContext.clearRect(0, 0, self.WIDTH, self.HEIGHT);
    self.canvasContext.fillStyle = "#333";
    self.canvasContext.fillRect(0, 0, self.WIDTH, self.HEIGHT);    
  }

}
