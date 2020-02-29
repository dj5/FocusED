
var ws = new WebSocket(location.href.replace('http', 'ws').replace('room', 'ws'));

var initiator;
var pc;
 var streamRecorder;
var recordedChunks = [];
var recorder;
var fcon=0;
function initiatorCtrl(event) {
    console.log(event.data);
    if (event.data == "fullhouse") {
        alert("full house");
    }
    if (event.data == "initiator") {
        initiator = false;
        init();
    }
    if (event.data == "not initiator") {
        initiator = true;
        init();
    }
}

ws.onmessage = initiatorCtrl;


function init() {
    var constraints = {
        audio: true,
        video: true
    };
//navigator.mediaDevices.getUserMedia(constraints,connect,fail);
   navigator.getUserMedia(constraints, connect, fail);
}


function connect(stream) {
    pc = new RTCPeerConnection(null);

    if (stream) {
        pc.addStream(stream);
	
        $('#local').attachStream(stream);
    }

    pc.onaddstream = function(event) {
        $('#remote').attachStream(event.stream);
	startRecording(stream);
        logStreaming(true,stream);
	
    };
    pc.onicecandidate = function(event) {
        if (event.candidate) {
            ws.send(JSON.stringify(event.candidate));
        }
    };
    ws.onmessage = function (event) {
        var signal = JSON.parse(event.data);
        if (signal.sdp) {
            if (initiator) {
                receiveAnswer(signal);
            } else {
                receiveOffer(signal);
            }
        } else if (signal.candidate) {
            pc.addIceCandidate(new RTCIceCandidate(signal));
        }
    };

    if (initiator) {
        createOffer();
    } else {
        log('waiting for offer...');
    }
    logStreaming(false);
}


function createOffer() {
    log('creating offer...');
    pc.createOffer(function(offer) {
        log('created offer...');
        pc.setLocalDescription(offer, function() {
            log('sending to remote...');
            ws.send(JSON.stringify(offer));
        }, fail);
    }, fail);
}


function receiveOffer(offer) {
    log('received offer...');
    pc.setRemoteDescription(new RTCSessionDescription(offer), function() {
        log('creating answer...');
        pc.createAnswer(function(answer) {
            log('created answer...');
            pc.setLocalDescription(answer, function() {
                log('sent answer');
                ws.send(JSON.stringify(answer));
            }, fail);
        }, fail);
    }, fail);
}


function receiveAnswer(answer) {
    log('received answer');
    pc.setRemoteDescription(new RTCSessionDescription(answer));
}


function log() {
    $('#status').text(Array.prototype.join.call(arguments, ' '));
    console.log.apply(console, arguments);
}


function logStreaming(streaming) {
    
    $('#streaming').text(streaming ? '[streaming]' : '[..]');
}

function blobToFile(theBlob, fileName){
    //A Blob() is almost a File() - it's just missing the two properties below which we will add
    theBlob.lastModifiedDate = new Date();
    theBlob.name = fileName;
    return theBlob;
}
function fail() {
    $('#status').text(Array.prototype.join.call(arguments, ' '));
    $('#status').addClass('error');
    console.error.apply(console, arguments);
}

  function startRecording(stream) {
console.log("start")
	streamRecorder = new MediaRecorder(stream)
        streamRecorder.start()
	streamRecorder.ondataavailable = handleDataAvailable;

        setTimeout(stopRecording, 12000,stream);
    }
 function stopRecording(stream) {
	console.log("calling save")
        //streamRecorder.requestData(postVideoToServer);
		//sdownload();
		streamRecorder.stop()
		startRecording(stream)
		//window.history.go(-1)
		//return false
    }
function handleDataAvailable(event) {
  console.log("data-available");
  if (event.data.size > 0) {
    recordedChunks.push(event.data);
    console.log(recordedChunks);
    download();
  } else {
    // ...
  }
}
function download() {
console.log(recordedChunks)
  var blob = new Blob(recordedChunks, {
	type: "video/mp4"
  });
    
var url = URL.createObjectURL(blob);
file=blobToFile(blob,"vid.mp4")
console.log(file)
postVideoToServer(url,blob)

 // var url = URL.createObjectURL(blob);
 // var a = document.createElement("a");
  //document.body.appendChild(a);
  //a.style = "display: none";
  //a.href = url;
 //a.download = "test.mp4";
 // a.click();
 // window.URL.revokeObjectURL(url);
}
 function postVideoToServer(url, videoblob) {
	console.log("posting")
        //var data = {};
        //data.data = videoblob;
	//data.url= url;
	//data.filename="videot.mp4";
	//data.processData= false;
        //data.metadata = 'test metadata';
        //data.action = "upload_video";
	console.log(videoblob)
	var fd = new FormData()
	var fname="v"+String(fcon);
	fcon=fcon+1;
	var files = new File([videoblob], fname+".mp4");
	fd.append('file', files);
	console.log(fd)	
	 $.ajax({ 
					url: 'http://127.0.0.1:5002/upload', 
					type: 'post', 
					data: fd, 
					contentType: false, 
					processData: false, 
					success: function(response){ 
						if(response != 0){ 
						alert('file uploaded'); 
						} 
						else{ 
							alert('file not uploaded'); 
						} 
					}, 
				}); 

        //jQuery.post("http://127.0.0.1:5002/upload", fd, onUploadSuccess);
    }
    function onUploadSuccess() {
        alert ('video uploaded');
    }

jQuery.fn.attachStream = function(stream) {
    this.each(function() {
//        this.src =stream;
         if (this.mozSrcObject !== undefined) { // FF18a
              this.mozSrcObject = stream;
            } else if (this.srcObject !== undefined) {
              this.srcObject = stream;
            } else { // FF16a, 17a
             this.src = stream;
            }
	//startRecording(stream);
        this.play();
	console.log("calling stream")
	//setTimeout(stopRecording, 9000,stream);
       //stopRecording();
	
    });
};
