Recorder.prototype.storePage = function( page ) {
  // CUSTOM STOREPAGE
  this.recordedPages.push( page );
  this.totalLength += page.length;

  // Stream is finished
  if ( page[5] & 4 ) {
    var outputData = new Uint8Array( this.totalLength );
    var outputIndex = 0;

    for ( var i = 0; i < this.recordedPages.length; i++ ) {
      outputData.set( this.recordedPages[i], outputIndex );
      outputIndex += this.recordedPages[i].length;
    }

    this.eventTarget.dispatchEvent( new CustomEvent( 'dataAvailable', {
      detail: outputData
    }));

    this.recordedPages = [];
    this.eventTarget.dispatchEvent( new Event( 'stop' ) );
  } else if (this.config.encoderPath.search('Wave') > 0){
    console.log('Using custom store page routine to send wave.');
    this.eventTarget.dispatchEvent( new CustomEvent( 'dataAvailable', {
      detail: page
    }));
  }
};