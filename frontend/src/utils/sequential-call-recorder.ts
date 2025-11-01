export class SequentialCallRecorder {
    private audioContext: AudioContext;
    private destination: MediaStreamAudioDestinationNode;
    private mediaRecorder: MediaRecorder | null = null;
    private userSource: MediaStreamAudioSourceNode | null = null;
    private aiGainNode: GainNode | null = null;
    private userGainNode: GainNode | null = null;
    private audioChunks: Blob[] = [];
    private isRecording: boolean = false;
    private sampleRate: number = 24000;
    
    // For AI audio playback
    private aiAudioQueue: AudioBuffer[] = [];
    private currentAISource: AudioBufferSourceNode | null = null;
    private isPlayingAI: boolean = false;
  
    constructor(sampleRate: number = 24000) {
      this.sampleRate = sampleRate;
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: this.sampleRate
      });
      
      // Create a destination that we can record from
      this.destination = this.audioContext.createMediaStreamDestination();
      
      // Create gain nodes for mixing
      this.userGainNode = this.audioContext.createGain();
      this.aiGainNode = this.audioContext.createGain();
      
      // Connect gain nodes to destination
      this.userGainNode.connect(this.destination);
      this.aiGainNode.connect(this.destination);
    }
  
    async startRecording(userStream: MediaStream): Promise<void> {
      this.audioChunks = [];
      this.isRecording = true;
  
      try {
        // Connect user microphone
        this.userSource = this.audioContext.createMediaStreamSource(userStream);
        this.userSource.connect(this.userGainNode!);
  
        // Create MediaRecorder from the destination stream
        const options: MediaRecorderOptions = {
          mimeType: 'audio/webm;codecs=opus',
          audioBitsPerSecond: 128000
        };
  
        // Try different mime types if webm is not supported
        if (!MediaRecorder.isTypeSupported(options.mimeType!)) {
          if (MediaRecorder.isTypeSupported('audio/webm')) {
            options.mimeType = 'audio/webm';
          } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
            options.mimeType = 'audio/ogg';
          } else {
            delete options.mimeType;
          }
        }
  
        this.mediaRecorder = new MediaRecorder(this.destination.stream, options);
  
        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };
  
        this.mediaRecorder.start(100); // Collect data every 100ms
        console.log('Sequential recording started with format:', this.mediaRecorder.mimeType);
      } catch (error) {
        console.error('Error starting recording:', error);
        throw error;
      }
    }
  
    // Add AI audio and play it through the recording stream
    async addAIAudio(pcm16Data: Uint8Array): Promise<void> {
      if (!this.isRecording) return;
  
      try {
        // Convert PCM16 to Float32Array
        const float32Array = new Float32Array(pcm16Data.length / 2);
        const dataView = new DataView(pcm16Data.buffer);
  
        for (let i = 0; i < pcm16Data.length / 2; i++) {
          const int16 = dataView.getInt16(i * 2, true);
          float32Array[i] = int16 / 32768;
        }
  
        // Create audio buffer
        const audioBuffer = this.audioContext.createBuffer(
          1,
          float32Array.length,
          this.sampleRate
        );
        audioBuffer.getChannelData(0).set(float32Array);
  
        this.aiAudioQueue.push(audioBuffer);
  
        if (!this.isPlayingAI) {
          this.playNextAIBuffer();
        }
      } catch (error) {
        console.error('Error adding AI audio:', error);
      }
    }
  
    private playNextAIBuffer(): void {
      if (this.aiAudioQueue.length === 0) {
        this.isPlayingAI = false;
        return;
      }
  
      this.isPlayingAI = true;
      const audioBuffer = this.aiAudioQueue.shift()!;
  
      const source = this.audioContext.createBufferSource();
      source.buffer = audioBuffer;
      
      // Connect to both the recording destination AND the speakers
      source.connect(this.aiGainNode!);
      
      this.currentAISource = source;
  
      source.onended = () => {
        if (this.aiAudioQueue.length > 0) {
          this.playNextAIBuffer();
        } else {
          this.isPlayingAI = false;
        }
      };
  
      source.start(0);
    }
  
    async stopRecording(): Promise<Blob> {
      return new Promise((resolve, reject) => {
        if (!this.mediaRecorder) {
          reject(new Error('No recording in progress'));
          return;
        }
  
        this.isRecording = false;
  
        this.mediaRecorder.onstop = async () => {
          try {
            // Clean up
            if (this.userSource) {
              this.userSource.disconnect();
            }
            if (this.currentAISource) {
              try {
                this.currentAISource.stop();
              } catch (e) {
                // Already stopped
              }
            }
  
            // Determine the mime type from recorded chunks
            let mimeType = 'audio/webm';
            if (this.audioChunks.length > 0) {
              mimeType = this.audioChunks[0].type;
            }
  
            const recordedBlob = new Blob(this.audioChunks, { type: mimeType });
            console.log('Recording captured:', recordedBlob.size, 'bytes, type:', mimeType);
  
            // Convert to WAV for backend compatibility
            const wavBlob = await this.convertToWav(recordedBlob);
            resolve(wavBlob);
          } catch (error) {
            reject(error);
          }
        };
  
        this.mediaRecorder.stop();
      });
    }
  
    private async convertToWav(blob: Blob): Promise<Blob> {
      try {
        const arrayBuffer = await blob.arrayBuffer();
        const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
  
        // Convert AudioBuffer to WAV
        return this.audioBufferToWav(audioBuffer);
      } catch (error) {
        console.error('Error converting to WAV:', error);
        // If conversion fails, return original blob
        return blob;
      }
    }
  
    private audioBufferToWav(audioBuffer: AudioBuffer): Blob {
      const numChannels = audioBuffer.numberOfChannels;
      const sampleRate = audioBuffer.sampleRate;
      const format = 1; // PCM
      const bitDepth = 16;
  
      // Interleave channels
      const length = audioBuffer.length * numChannels;
      const buffer = new ArrayBuffer(44 + length * 2);
      const view = new DataView(buffer);
  
      const writeString = (offset: number, string: string) => {
        for (let i = 0; i < string.length; i++) {
          view.setUint8(offset + i, string.charCodeAt(i));
        }
      };
  
      // RIFF chunk descriptor
      writeString(0, 'RIFF');
      view.setUint32(4, 36 + length * 2, true);
      writeString(8, 'WAVE');
  
      // fmt sub-chunk
      writeString(12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, format, true);
      view.setUint16(22, numChannels, true);
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate * numChannels * bitDepth / 8, true);
      view.setUint16(32, numChannels * bitDepth / 8, true);
      view.setUint16(34, bitDepth, true);
  
      // data sub-chunk
      writeString(36, 'data');
      view.setUint32(40, length * 2, true);
  
      // Write interleaved audio data
      const channels = [];
      for (let i = 0; i < numChannels; i++) {
        channels.push(audioBuffer.getChannelData(i));
      }
  
      let offset = 44;
      for (let i = 0; i < audioBuffer.length; i++) {
        for (let channel = 0; channel < numChannels; channel++) {
          const sample = Math.max(-1, Math.min(1, channels[channel][i]));
          const int16 = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
          view.setInt16(offset, int16, true);
          offset += 2;
        }
      }
  
      return new Blob([buffer], { type: 'audio/wav' });
    }
  
    isCurrentlyRecording(): boolean {
      return this.isRecording;
    }
  
    async cleanup(): Promise<void> {
      if (this.audioContext.state !== 'closed') {
        await this.audioContext.close();
      }
    }
  }