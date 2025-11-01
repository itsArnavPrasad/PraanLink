export class AudioStreamer {
    constructor(audioContext) {
      this.context = audioContext;
      this.sampleRate = 24000;
      this.audioQueue = [];
      this.isPlaying = false;
      this.currentSource = null;
      this.gainNode = this.context.createGain();
      this.gainNode.connect(this.context.destination);
      this.onComplete = () => {};
      this.playbackTimeout = null;
      this.lastPlaybackTime = 0;
    }
  
    addPCM16(chunk) {
      const float32Array = new Float32Array(chunk.length / 2);
      const dataView = new DataView(chunk.buffer);
  
      for (let i = 0; i < chunk.length / 2; i++) {
        try {
          const int16 = dataView.getInt16(i * 2, true);
          float32Array[i] = int16 / 32768;
        } catch (e) {
          console.error(e);
        }
      }
  
      const audioBuffer = this.context.createBuffer(1, float32Array.length, this.sampleRate);
      audioBuffer.getChannelData(0).set(float32Array);
  
      this.audioQueue.push(audioBuffer);
      
      if (!this.isPlaying) {
        this.isPlaying = true;
        this.lastPlaybackTime = this.context.currentTime;
        this.playNextBuffer();
      }
  
      this.checkPlaybackStatus();
    }
  
    checkPlaybackStatus() {
      if (this.playbackTimeout) {
        clearTimeout(this.playbackTimeout);
      }
  
      this.playbackTimeout = setTimeout(() => {
        const now = this.context.currentTime;
        const timeSinceLastPlayback = now - this.lastPlaybackTime;
  
        if (timeSinceLastPlayback > 1 && this.audioQueue.length > 0 && this.isPlaying) {
          console.log('Playback appears to have stalled, restarting...');
          this.playNextBuffer();
        }
  
        if (this.isPlaying) {
          this.checkPlaybackStatus();
        }
      }, 1000);
    }
  
    playNextBuffer() {
      if (this.audioQueue.length === 0) {
        this.isPlaying = false;
        return;
      }
  
      this.lastPlaybackTime = this.context.currentTime;
  
      try {
        const audioBuffer = this.audioQueue.shift();
        const source = this.context.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.gainNode);
  
        if (this.currentSource) {
          try {
            this.currentSource.disconnect();
          } catch (e) {
            // Ignore disconnection errors
          }
        }
        this.currentSource = source;
  
        source.onended = () => {
          this.lastPlaybackTime = this.context.currentTime;
          if (this.audioQueue.length > 0) {
            setTimeout(() => this.playNextBuffer(), 0);
          } else {
            this.isPlaying = false;
            this.onComplete();
          }
        };
  
        source.start(0);
      } catch (error) {
        console.error('Error during playback:', error);
        if (this.audioQueue.length > 0) {
          setTimeout(() => this.playNextBuffer(), 100);
        } else {
          this.isPlaying = false;
        }
      }
    }
  
    stop() {
      this.isPlaying = false;
      if (this.playbackTimeout) {
        clearTimeout(this.playbackTimeout);
        this.playbackTimeout = null;
      }
      if (this.currentSource) {
        try {
          this.currentSource.stop();
          this.currentSource.disconnect();
        } catch (e) {
          // Ignore if already stopped
        }
      }
      this.audioQueue = [];
      this.gainNode.gain.linearRampToValueAtTime(0, this.context.currentTime + 0.1);
  
      setTimeout(() => {
        this.gainNode.disconnect();
        this.gainNode = this.context.createGain();
        this.gainNode.connect(this.context.destination);
      }, 200);
    }
  
    async resume() {
      if (this.context.state === 'suspended') {
        await this.context.resume();
      }
      this.lastPlaybackTime = this.context.currentTime;
      this.gainNode.gain.setValueAtTime(1, this.context.currentTime);
      if (this.audioQueue.length > 0 && !this.isPlaying) {
        this.isPlaying = true;
        this.playNextBuffer();
      }
    }
  
    complete() {
      if (this.audioQueue.length > 0) {
        return;
      }
      if (this.playbackTimeout) {
        clearTimeout(this.playbackTimeout);
        this.playbackTimeout = null;
      }
      this.onComplete();
    }
  }