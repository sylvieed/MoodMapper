let modelsLoaded = false;
let lastExpressions = null;
var interval = 1000;

function sendMood() {
    console.log("Sending moods to server")
    
    if (lastExpressions != null) {
        expressions = JSON.stringify(lastExpressions)
        $.post( "/save_mood", {
            expressions: expressions,
            complete: function () {
                console.log("Sent moods, running again in " + interval + "ms")
                // Send the mood again after 1 second
                setTimeout(sendMood, interval);
            }
        });
    } else {
        console.log("No mood detected, running again in " + interval + "ms")
        // Send the mood again after 1 second
        setTimeout(sendMood, interval);
    }
}

function isFaceDetectionModelLoaded() {
    return !!(faceapi.nets.tinyFaceDetector).params
}

async function onPlay() {
    const videoEl = $('#inputVideo').get(0)

    if(videoEl.paused || videoEl.ended || !isFaceDetectionModelLoaded() || !modelsLoaded){
        return setTimeout(() => onPlay())
    }

    // let inputSize = 512
    // let scoreThreshold = 0.5
    const options = new faceapi.TinyFaceDetectorOptions()
    const result = await faceapi.detectSingleFace(videoEl, options).withFaceExpressions()
    
    if (result) {
        lastExpressions = result.expressions
        const canvas = $('#overlay').get(0)
        const dims = faceapi.matchDimensions(canvas, videoEl, true)

        const resizedResult = faceapi.resizeResults(result, dims)
        const minConfidence = 0.05
        faceapi.draw.drawDetections(canvas, resizedResult)
        faceapi.draw.drawFaceExpressions(canvas, resizedResult, minConfidence)
    } else {
        lastExpressions = null;
    }

    setTimeout(() => onPlay())
}
            
async function run(){

    // try to access users webcam and stream the images
    // to the video element
    const stream = await navigator.mediaDevices.getUserMedia({ video: {} })
    const videoEl = $('#inputVideo').get(0)
    videoEl.srcObject = stream
    
    await faceapi.loadTinyFaceDetectorModel('static/models')
    await faceapi.loadFaceExpressionModel('static/models')
    
    modelsLoaded = true;
    console.log("Models Loaded")
}

$(document).ready(function() {
    run()
    sendMood()
})
