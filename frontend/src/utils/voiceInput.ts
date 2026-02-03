/**
 * Voice Input Utility for the Todo App
 * Provides speech recognition functionality to convert voice commands to text
 */

interface VoiceInputOptions {
  lang?: string;
  interimResults?: boolean;
  continuous?: boolean;
}

interface VoiceInputResult {
  transcript: string;
  isFinal: boolean;
}

class VoiceInputManager {
  private recognition: any;
  private isListening: boolean = false;
  private callbacks: {
    onResult?: (result: VoiceInputResult) => void;
    onError?: (error: string) => void;
    onStart?: () => void;
    onStop?: () => void;
  } = {};

  constructor(options: VoiceInputOptions = {}) {
    // Check if browser supports speech recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      throw new Error('Speech recognition is not supported in this browser');
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = options.continuous ?? false;
    this.recognition.interimResults = options.interimResults ?? true;
    this.recognition.lang = options.lang ?? 'en-US';

    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0])
        .map(result => result.transcript)
        .join('');

      const isFinal = event.results[event.results.length - 1].isFinal;

      if (this.callbacks.onResult) {
        this.callbacks.onResult({
          transcript,
          isFinal
        });
      }
    };

    this.recognition.onerror = (event: any) => {
      const errorMessage = event.error || 'Unknown error occurred';

      if (this.callbacks.onError) {
        this.callbacks.onError(errorMessage);
      }
    };

    this.recognition.onstart = () => {
      this.isListening = true;
      if (this.callbacks.onStart) {
        this.callbacks.onStart();
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (this.callbacks.onStop) {
        this.callbacks.onStop();
      }
    };
  }

  public start(callbacks?: {
    onResult?: (result: VoiceInputResult) => void;
    onError?: (error: string) => void;
    onStart?: () => void;
    onStop?: () => void;
  }) {
    if (callbacks) {
      this.callbacks = callbacks;
    }

    try {
      this.recognition.start();
    } catch (error: any) {
      if (this.callbacks.onError) {
        this.callbacks.onError(error.message || 'Failed to start voice recognition');
      }
    }
  }

  public stop() {
    if (this.isListening) {
      this.recognition.stop();
    }
  }

  public abort() {
    if (this.isListening) {
      this.recognition.abort();
    }
  }

  public isSupported(): boolean {
    return !!this.recognition;
  }

  public isCurrentlyListening(): boolean {
    return this.isListening;
  }
}

export default VoiceInputManager;