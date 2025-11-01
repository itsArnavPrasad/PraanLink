// Simple EventEmitter implementation
class EventEmitter {
    constructor() {
      this.events = {};
    }
  
    on(event, listener) {
      if (!this.events[event]) {
        this.events[event] = [];
      }
      this.events[event].push(listener);
    }
  
    off(event, listenerToRemove) {
      if (!this.events[event]) return;
      this.events[event] = this.events[event].filter(listener => listener !== listenerToRemove);
    }
  
    emit(event, ...args) {
      if (!this.events[event]) return;
      this.events[event].forEach(listener => listener(...args));
    }
  }
  
  function arrayBufferToBase64(buffer) {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }
  
  const AudioRecordingWorklet = `
  class AudioProcessingWorklet extends AudioWorkletProcessor {
    buffer = new Int16Array(2048);
    bufferWriteIndex = 0;
  
    constructor() {
      super();
    }
  
    process(inputs) {
      if (inputs[0].length) {
        const channel0 = inputs[0][0];
        this.processChunk(channel0);
      }
      return true;
    }
  
    sendAndClearBuffer() {
      this.port.postMessage({
        event: "chunk",
        data: {
          int16arrayBuffer: this.buffer.slice(0, this.bufferWriteIndex).buffer,
        },
      });
      this.bufferWriteIndex = 0;
    }
  
    processChunk(float32Array) {
      const l = float32Array.length;
      
      for (let i = 0; i < l; i++) {
        const int16Value = float32Array[i] * 32768;
        this.buffer[this.bufferWriteIndex++] = int16Value;
        if(this.bufferWriteIndex >= this.buffer.length) {
          this.sendAndClearBuffer();
        }
      }
  
      if(this.bufferWriteIndex >= this.buffer.length) {
        this.sendAndClearBuffer();
      }
    }
  }
  
  registerProcessor('audio-recorder-worklet', AudioProcessingWorklet);
  `;
  
  export class AudioRecorder extends EventEmitter {
    constructor() {
      super();
      this.sampleRate = 16000;
      this.stream = undefined;
      this.audioContext = undefined;
      this.source = undefined;
      this.recording = false;
      this.recordingWorklet = undefined;
      this.starting = null;
      this.isMuted = false;
      this.workletRegistered = false;
    }
  
    async start() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Could not request user media");
      }
  
      this.starting = new Promise(async (resolve, reject) => {
        try {
          this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ 
            sampleRate: this.sampleRate 
          });
          this.source = this.audioContext.createMediaStreamSource(this.stream);
  
          if (!this.workletRegistered) {
            const blob = new Blob([AudioRecordingWorklet], { type: 'application/javascript' });
            const workletUrl = URL.createObjectURL(blob);
            await this.audioContext.audioWorklet.addModule(workletUrl);
            this.workletRegistered = true;
          }
  
          this.recordingWorklet = new AudioWorkletNode(this.audioContext, 'audio-recorder-worklet');
  
          this.recordingWorklet.port.onmessage = async (ev) => {
            const arrayBuffer = ev.data.data.int16arrayBuffer;
            if (arrayBuffer) {
              const arrayBufferString = arrayBufferToBase64(arrayBuffer);
              this.emit("data", arrayBufferString);
            }
          };
  
          this.source.connect(this.recordingWorklet);
          this.recording = true;
          resolve();
          this.starting = null;
        } catch (error) {
          reject(error);
        }
      });
  
      return this.starting;
    }
  
    stop() {
      const handleStop = () => {
        this.source?.disconnect();
        this.stream?.getTracks().forEach((track) => track.stop());
        this.stream = undefined;
        this.recordingWorklet = undefined;
        this.recording = false;
      };
      
      if (this.starting) {
        this.starting.then(handleStop);
        return;
      }
      handleStop();
    }
  }