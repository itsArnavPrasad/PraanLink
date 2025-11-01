import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Mic, Square, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export default function CheckIn() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const mockTranscripts = [
    "I've been feeling a bit tired lately, especially in the afternoons.",
    "My sleep has been okay, around 6-7 hours per night.",
    "I did have a headache yesterday, but it went away after some rest.",
    "Overall, I feel pretty good today.",
  ];

  const handleStartRecording = () => {
    setIsRecording(true);
    setTranscript([]);
    toast.success("Recording started");

    // Simulate transcription every 3 seconds
    let index = 0;
    const addTranscript = () => {
      if (index < mockTranscripts.length) {
        setTranscript((prev) => [...prev, mockTranscripts[index]]);
        index++;
        timeoutRef.current = setTimeout(addTranscript, 3000);
      } else {
        handleStopRecording();
      }
    };
    timeoutRef.current = setTimeout(addTranscript, 2000);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    setIsProcessing(true);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);

    setTimeout(() => {
      setIsProcessing(false);
      toast.success("Recording processed successfully");
    }, 1500);
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-8 py-6">
        <h1 className="text-3xl font-bold text-foreground">Daily Check-In</h1>
        <p className="mt-2 text-muted-foreground">
          Share how you're feeling today. Your voice matters.
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">
        <div className="mx-auto max-w-3xl space-y-6">
          {/* Recording Interface */}
          <Card className="p-8">
            <div className="flex flex-col items-center space-y-6">
              {/* Mic Button */}
              <button
                onClick={isRecording ? handleStopRecording : handleStartRecording}
                disabled={isProcessing}
                className={cn(
                  "relative flex h-32 w-32 items-center justify-center rounded-full transition-smooth",
                  isRecording
                    ? "bg-destructive shadow-lg shadow-destructive/30 animate-pulse"
                    : "bg-primary shadow-md hover:shadow-lg hover:scale-105",
                  isProcessing && "opacity-50 cursor-not-allowed"
                )}
              >
                {isProcessing ? (
                  <Loader2 className="h-12 w-12 text-primary-foreground animate-spin" />
                ) : isRecording ? (
                  <Square className="h-12 w-12 text-destructive-foreground" />
                ) : (
                  <Mic className="h-12 w-12 text-primary-foreground" />
                )}
                
                {isRecording && (
                  <span className="absolute -bottom-2 -right-2 flex h-6 w-6">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-destructive opacity-75"></span>
                    <span className="relative inline-flex h-6 w-6 rounded-full bg-destructive"></span>
                  </span>
                )}
              </button>

              <div className="text-center">
                <p className="text-lg font-medium text-foreground">
                  {isProcessing
                    ? "Processing your recording..."
                    : isRecording
                    ? "Listening... Tap to stop"
                    : "Tap to start recording"}
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  {isRecording && "Speak naturally about your health"}
                </p>
              </div>
            </div>
          </Card>

          {/* Transcript Display */}
          {transcript.length > 0 && (
            <Card className="p-6">
              <h3 className="mb-4 text-lg font-semibold text-foreground">
                Live Transcription
              </h3>
              <div className="space-y-3">
                {transcript.map((text, index) => (
                  <div
                    key={index}
                    className="rounded-lg bg-primary-lighter p-4 animate-in fade-in slide-in-from-bottom-2 duration-500"
                  >
                    <p className="text-sm text-foreground">{text}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Tips Card */}
          {!isRecording && transcript.length === 0 && (
            <Card className="p-6 bg-muted/50">
              <h3 className="mb-3 text-lg font-semibold text-foreground">
                Tips for Check-In
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Share your physical symptoms or discomfort</li>
                <li>• Mention your sleep quality and energy levels</li>
                <li>• Talk about any medication you've taken</li>
                <li>• Describe your mood and mental well-being</li>
              </ul>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
