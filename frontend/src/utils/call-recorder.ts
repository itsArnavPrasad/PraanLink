export class CallRecorder {
    private audioChunks: { type: 'user' | 'ai'; data: Float32Array; timestamp: number }[] = [];
    private mediaRecorder: MediaRecorder | null = null;
    private userStream: MediaStream | null = null;
    private userAudioContext: AudioContext | null = null;
    private userProcessor: ScriptProcessorNode | null = null;
    private sampleRate: number = 24000;
    private isRecording: boolean = false;
    private startTime: number = 0;
  
    constructor(sampleRate: number = 24000) {
      this.sampleRate = sampleRate;
    }
  
    async startRecording(userStream: MediaStream): Promise<void> {
      this.audioChunks = [];
      this.userStream = userStream;
      this.isRecording = true;
      this.startTime = Date.now();
  
      try {
        // Create audio context for user audio
        this.userAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
          sampleRate: this.sampleRate
        });
  
        const source = this.userAudioContext.createMediaStreamSource(userStream);
        
        // Use ScriptProcessorNode to capture user audio in real-time
        const bufferSize = 4096;
        this.userProcessor = this.userAudioContext.createScriptProcessor(bufferSize, 1, 1);
  
        this.userProcessor.onaudioprocess = (e) => {
          if (!this.isRecording) return;
          
          const inputData = e.inputBuffer.getChannelData(0);
          const chunk = new Float32Array(inputData);
          
          this.audioChunks.push({
            type: 'user',
            data: chunk,
            timestamp: Date.now() - this.startTime
          });
        };
  
        source.connect(this.userProcessor);
        this.userProcessor.connect(this.userAudioContext.destination);
  
        console.log('Sequential recording started');
      } catch (error) {
        console.error('Error starting recording:', error);
        throw error;
      }
    }
  
    // Call this method when AI audio is received
    addAIAudio(pcm16Data: Uint8Array): void {
      if (!this.isRecording) return;
  
      // Convert PCM16 to Float32Array
      const float32Array = new Float32Array(pcm16Data.length / 2);
      const dataView = new DataView(pcm16Data.buffer);
  
      for (let i = 0; i < pcm16Data.length / 2; i++) {
        const int16 = dataView.getInt16(i * 2, true);
        float32Array[i] = int16 / 32768;
      }
  
      this.audioChunks.push({
        type: 'ai',
        data: float32Array,
        timestamp: Date.now() - this.startTime
      });
    }
  
    async stopRecording(): Promise<Blob> {
      return new Promise(async (resolve, reject) => {
        try {
          this.isRecording = false;
  
          // Stop user audio capture
          if (this.userProcessor) {
            this.userProcessor.disconnect();
            this.userProcessor = null;
          }
  
          if (this.userAudioContext) {
            await this.userAudioContext.close();
            this.userAudioContext = null;
          }
  
          if (this.userStream) {
            this.userStream.getTracks().forEach(track => track.stop());
            this.userStream = null;
          }
  
          // Sort chunks by timestamp to ensure chronological order
          this.audioChunks.sort((a, b) => a.timestamp - b.timestamp);
  
          console.log(`Total chunks: ${this.audioChunks.length}`);
          console.log(`User chunks: ${this.audioChunks.filter(c => c.type === 'user').length}`);
          console.log(`AI chunks: ${this.audioChunks.filter(c => c.type === 'ai').length}`);
  
          // Calculate total length
          let totalLength = 0;
          for (const chunk of this.audioChunks) {
            totalLength += chunk.data.length;
          }
  
          if (totalLength === 0) {
            reject(new Error('No audio data recorded'));
            return;
          }
  
          // Create a single buffer with all audio in chronological order
          const fullAudio = new Float32Array(totalLength);
          let offset = 0;
  
          for (const chunk of this.audioChunks) {
            fullAudio.set(chunk.data, offset);
            offset += chunk.data.length;
          }
  
          // Convert to WAV
          const wavBlob = this.createWavBlob(fullAudio);
          console.log('WAV created:', wavBlob.size, 'bytes');
          
          resolve(wavBlob);
        } catch (error) {
          reject(error);
        }
      });
    }
  
    private createWavBlob(audioData: Float32Array): Blob {
      const numChannels = 1;
      const sampleRate = this.sampleRate;
      const format = 1; // PCM
      const bitDepth = 16;
  
      const dataLength = audioData.length * 2; // 16-bit = 2 bytes per sample
      const buffer = new ArrayBuffer(44 + dataLength);
      const view = new DataView(buffer);
  
      // Write WAV header
      const writeString = (offset: number, string: string) => {
        for (let i = 0; i < string.length; i++) {
          view.setUint8(offset + i, string.charCodeAt(i));
        }
      };
  
      // RIFF chunk descriptor
      writeString(0, 'RIFF');
      view.setUint32(4, 36 + dataLength, true);
      writeString(8, 'WAVE');
  
      // fmt sub-chunk
      writeString(12, 'fmt ');
      view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
      view.setUint16(20, format, true); // AudioFormat (1 for PCM)
      view.setUint16(22, numChannels, true); // NumChannels
      view.setUint32(24, sampleRate, true); // SampleRate
      view.setUint32(28, sampleRate * numChannels * bitDepth / 8, true); // ByteRate
      view.setUint16(32, numChannels * bitDepth / 8, true); // BlockAlign
      view.setUint16(34, bitDepth, true); // BitsPerSample
  
      // data sub-chunk
      writeString(36, 'data');
      view.setUint32(40, dataLength, true);
  
      // Write audio data
      let offset = 44;
      for (let i = 0; i < audioData.length; i++) {
        const sample = Math.max(-1, Math.min(1, audioData[i]));
        const int16 = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
        view.setInt16(offset, int16, true);
        offset += 2;
      }
  
      return new Blob([buffer], { type: 'audio/wav' });
    }
  
    isCurrentlyRecording(): boolean {
      return this.isRecording;
    }
  }