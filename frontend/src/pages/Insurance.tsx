import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Mic, Square, CheckCircle2, Shield, Users, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { GeminiLiveAPI } from "@/utils/gemini-live-api";
import { AudioRecorder } from "@/utils/audio-recorder";
import { AudioStreamer } from "@/utils/audio-streamer";
import { SequentialCallRecorder } from "@/utils/sequential-call-recorder";

interface InsurancePlan {
  id: number;
  provider: string;
  name: string;
  coverage: string;
  premium: string;
  features: string[];
  match: number;
}

const insurancePlans: InsurancePlan[] = [
  {
    id: 1,
    provider: "Star Health",
    name: "Comprehensive Health Plus",
    coverage: "₹10 Lakh",
    premium: "₹15,000/year",
    features: [
      "Cashless hospitalization",
      "Pre & post hospitalization",
      "Day-care procedures",
      "No room rent limit",
    ],
    match: 95,
  },
  {
    id: 2,
    provider: "HDFC ERGO",
    name: "Health Suraksha Gold",
    coverage: "₹7.5 Lakh",
    premium: "₹12,500/year",
    features: [
      "Cashless treatment",
      "Annual health check-up",
      "Pre-existing diseases covered",
      "Restore benefit",
    ],
    match: 88,
  },
  {
    id: 3,
    provider: "ICICI Lombard",
    name: "Complete Health Insurance",
    coverage: "₹5 Lakh",
    premium: "₹9,000/year",
    features: [
      "Ambulance charges covered",
      "Day-care treatments",
      "Wellness benefits",
      "Network hospitals",
    ],
    match: 82,
  },
];

export default function Insurance() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [recommendedPlans] = useState<InsurancePlan[]>(insurancePlans);

  const geminiAPIRef = useRef<any>(null);
  const audioRecorderRef = useRef<any>(null);
  const audioStreamerRef = useRef<any>(null);
  const callRecorderRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const initializedRef = useRef(false);

  // Replace with your actual API key
  const API_KEY = 'AIzaSyBOZvLU8kGhhY_d7dVeO63bucV1RNKJbVU';
  const endpoint = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${API_KEY}`;

  // Replace with your backend URL
  const BACKEND_URL = 'http://localhost:8000';

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording) {
      interval = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  // Initialize Gemini API
  useEffect(() => {
    const systemInstruction = `You are a knowledgeable and friendly health insurance advisor helping users find the perfect insurance plan for themselves and their families.

YOUR ROLE:
- You are an expert insurance consultant who understands health insurance products and helps people protect their health and financial wellbeing
- You help users understand the importance of health insurance and guide them to choose the right plan
- You analyze their age, family situation, health conditions, and budget to recommend the most suitable plan
- You speak naturally in a warm, trustworthy, and conversational manner

AVAILABLE INSURANCE PLANS:
You have access to these three insurance plans to recommend:

PLAN 1: Star Health - Comprehensive Health Plus
- Coverage: ₹10 Lakh
- Premium: ₹15,000/year
- Best for: Families with higher coverage needs, those wanting premium features
- Key Features:
  • Cashless hospitalization across 14,000+ network hospitals
  • Pre & post hospitalization coverage (60 days pre, 180 days post)
  • Day-care procedures covered
  • No room rent limit (can choose any room type)
  • Maternity coverage (after 2 year waiting period)
  • Annual health check-ups included
- Ideal for: Middle to upper middle-class families, those with aging parents, families planning for maternity

PLAN 2: HDFC ERGO - Health Suraksha Gold
- Coverage: ₹7.5 Lakh
- Premium: ₹12,500/year
- Best for: Individuals and small families, those with pre-existing conditions
- Key Features:
  • Cashless treatment at 10,000+ hospitals
  • Annual health check-up for preventive care
  • Pre-existing diseases covered (after 2-3 year waiting period)
  • Restore benefit - coverage amount restored if exhausted
  • Ambulance charges covered
  • AYUSH treatments covered
- Ideal for: Young professionals, nuclear families, people with pre-existing conditions like diabetes or hypertension

PLAN 3: ICICI Lombard - Complete Health Insurance
- Coverage: ₹5 Lakh
- Premium: ₹9,000/year
- Best for: Young individuals, budget-conscious buyers, those seeking basic coverage
- Key Features:
  • Ambulance charges covered
  • Day-care treatments for 150+ procedures
  • Wellness benefits and health coaching
  • Access to 7,000+ network hospitals
  • Domiciliary hospitalization for home treatment
  • Organ donor expenses covered
- Ideal for: Singles, young couples without kids, those starting their insurance journey, tight budgets

CONVERSATION APPROACH:
1. Start with a warm greeting and explain you're here to help them find the right health insurance
2. Emphasize why health insurance is crucial:
   - Medical costs are rising rapidly in India (15-20% annually)
   - A single hospitalization can wipe out years of savings
   - Family protection and financial security
   - Tax benefits under Section 80D
   - Cashless treatment reduces stress during emergencies

3. Ask thoughtful questions to understand their needs:
   - "Tell me about yourself - what's your age and do you have a family?"
   - "Are there any ongoing health conditions or concerns in your family?"
   - "How many family members would you like to cover?"
   - "Do you have elderly parents who need coverage?"
   - "What's your comfortable budget for annual premium?"
   - "Are you looking for extensive coverage or basic protection?"
   - "Any specific concerns like maternity, pre-existing conditions, or critical illness?"

4. Based on their answers, recommend the MOST SUITABLE plan:
   - For young singles/couples with limited budget → ICICI Lombard (Plan 3)
   - For families with pre-existing conditions → HDFC ERGO (Plan 2)
   - For larger families needing comprehensive coverage → Star Health (Plan 1)
   - For those with aging parents → Star Health or HDFC ERGO
   - For maternity planning → Star Health (Plan 1)

5. Explain your recommendation clearly:
   - Why this specific plan suits their situation
   - What makes it the right choice for their needs
   - What they should be aware of (waiting periods, exclusions)
   - How it provides value for their premium

6. Be honest about trade-offs:
   - Higher coverage means higher premium
   - Lower premium might mean some limitations
   - Waiting periods for certain conditions
   - Network hospital limitations

IMPORTANT GUIDELINES:
- Always emphasize the importance of health insurance early in the conversation
- Use real-life examples to illustrate why insurance matters
- Be empathetic and understanding about budget concerns
- Never pressure - educate and empower them to make informed decisions
- Keep explanations simple and avoid insurance jargon
- Be transparent about what's covered and what's not
- Recommend ONLY ONE plan as the best fit, but mention alternatives if asked
- Show genuine care for their wellbeing and financial security

Remember: Your goal is to help them understand why health insurance is essential and guide them to the plan that truly fits their life situation, not just sell them the most expensive option.

Begin by warmly greeting them and asking about their current insurance status and what brings them here today.`;

    const customSetupConfig = {
      model: "models/gemini-2.0-flash-exp",
      system_instruction: {
        parts: [{
          text: systemInstruction
        }]
      },
      generation_config: {
        response_modalities: ["audio"],
        speech_config: {
          voice_config: {
            prebuilt_voice_config: {
              voice_name: "Charon"
            }
          }
        }
      }
    };

    geminiAPIRef.current = new GeminiLiveAPI(endpoint, true, customSetupConfig);

    geminiAPIRef.current.onSetupComplete = () => {
      console.log('Gemini API setup complete');
    };

    geminiAPIRef.current.onAudioData = async (audioData: string) => {
      if (!audioStreamerRef.current?.isPlaying) {
        setIsAISpeaking(true);
      }
      
      const arrayBuffer = base64ToArrayBuffer(audioData);
      const uint8Array = new Uint8Array(arrayBuffer);
      
      if (callRecorderRef.current) {
        callRecorderRef.current.addAIAudio(uint8Array);
      }
      
      await playAudioChunk(audioData);
    };

    geminiAPIRef.current.onInterrupted = () => {
      console.log('AI interrupted');
      setIsAISpeaking(false);
      audioStreamerRef.current?.stop();
    };

    geminiAPIRef.current.onTurnComplete = () => {
      console.log('AI finished speaking');
      setIsAISpeaking(false);
      audioStreamerRef.current?.complete();
    };

    geminiAPIRef.current.onError = (message: string) => {
      console.error('Gemini API error:', message);
      toast.error(message);
    };

    return () => {
      if (audioRecorderRef.current) {
        audioRecorderRef.current.stop();
      }
      if (audioStreamerRef.current) {
        audioStreamerRef.current.stop();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  const ensureAudioInitialized = async () => {
    if (!initializedRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ 
        sampleRate: 24000 
      });
      audioStreamerRef.current = new AudioStreamer(audioContextRef.current);
      await audioContextRef.current.resume();
      initializedRef.current = true;
      console.log('Audio context initialized:', audioContextRef.current.state);
    }
  };

  const base64ToArrayBuffer = (base64: string) => {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  };

  const playAudioChunk = async (base64AudioChunk: string) => {
    try {
      await ensureAudioInitialized();
      const arrayBuffer = base64ToArrayBuffer(base64AudioChunk);
      const uint8Array = new Uint8Array(arrayBuffer);
      audioStreamerRef.current?.addPCM16(uint8Array);
      audioStreamerRef.current?.resume();
    } catch (error) {
      console.error('Error queuing audio chunk:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const startRecording = async () => {
    try {
      await ensureAudioInitialized();

      audioStreamerRef.current?.stop();

      if (geminiAPIRef.current.ws.readyState !== WebSocket.OPEN) {
        toast.error("Connection not ready. Please wait...");
        return;
      }

      audioRecorderRef.current = new AudioRecorder();
      await audioRecorderRef.current.start();

      audioRecorderRef.current.on('data', (base64Data: string) => {
        geminiAPIRef.current?.sendAudioChunk(base64Data);
      });

      callRecorderRef.current = new SequentialCallRecorder(24000);
      
      const userStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      await callRecorderRef.current.startRecording(userStream);

      setIsRecording(true);
      setElapsed(0);
      toast.success("Insurance advisor is listening...");

    } catch (error: any) {
      console.error('Error starting recording:', error);
      toast.error('Error starting conversation: ' + error.message);
    }
  };

  const stopRecording = async () => {
    setIsProcessing(true);
    
    try {
      if (audioRecorderRef.current) {
        audioRecorderRef.current.stop();
        audioRecorderRef.current.off('data');
      }

      let recordingBlob: Blob | null = null;
      if (callRecorderRef.current && callRecorderRef.current.isCurrentlyRecording()) {
        recordingBlob = await callRecorderRef.current.stopRecording();
        console.log('Recording captured:', recordingBlob.size, 'bytes');
      }

      geminiAPIRef.current?.sendEndMessage();

      setIsRecording(false);

      if (recordingBlob) {
        toast.loading("Saving conversation...");
        
        const formData = new FormData();
        const fileName = `insurance_consultation_${Date.now()}.wav`;
        formData.append('file', recordingBlob, fileName);

        const response = await fetch(`${BACKEND_URL}/upload-insurance-consultation`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          toast.success("Consultation saved successfully!");
          console.log('Consultation saved:', data);
        } else {
          toast.error("Failed to save consultation");
        }
      }
    } catch (error: any) {
      console.error('Error ending consultation:', error);
      toast.error('Error ending consultation: ' + error.message);
    } finally {
      setIsProcessing(false);
      setElapsed(0);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Voice Agent Button - Top */}
      <div className="border-b border-border bg-card px-6 py-6">
        <div className="flex flex-col items-center gap-4">
          <div className="text-center">
            <h2 className="text-xl font-bold text-foreground mb-1">
              Insurance Assistant
            </h2>
            <p className="text-sm text-muted-foreground">
              {isRecording 
                ? `Consultation in progress - ${formatTime(elapsed)}`
                : "Tap to speak with your personal insurance advisor"}
            </p>
          </div>

          {/* Audio Visualizer */}
          <AnimatePresence>
            {isRecording && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex justify-center gap-1 h-12 items-end mb-2"
              >
                {[...Array(12)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{
                      height: [
                        "20%",
                        `${Math.random() * 80 + 20}%`,
                        "20%",
                      ],
                    }}
                    transition={{
                      repeat: Infinity,
                      duration: 0.8,
                      delay: i * 0.05,
                    }}
                    className="w-1.5 bg-gradient-to-t from-primary to-secondary rounded-full"
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
          
          <Button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            size="lg"
            className={`h-20 w-20 rounded-full ${
              isRecording ? "bg-destructive hover:bg-destructive/90 animate-pulse" : ""
            }`}
          >
            {isProcessing ? (
              <Loader2 className="h-8 w-8 animate-spin" />
            ) : isRecording ? (
              <Square className="h-8 w-8" />
            ) : (
              <Mic className="h-8 w-8" />
            )}
          </Button>

          {isAISpeaking && (
            <motion.div
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="flex items-center gap-2 text-primary font-medium text-sm"
            >
              <div className="w-2 h-2 rounded-full bg-primary" />
              Advisor is speaking...
            </motion.div>
          )}
        </div>
      </div>

      {/* Insurance Plans - Below */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <div className="border-b border-border bg-card px-6 py-5">
          <h2 className="text-xl font-bold text-foreground">
            Available Plans
          </h2>
          <p className="text-sm text-muted-foreground">
            Talk to our advisor to find the best plan for you
          </p>
        </div>

        {/* Plans List */}
        <div className="flex-1 overflow-auto p-6">
          <div className="space-y-4">
            {recommendedPlans.map((plan) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="p-5 transition-smooth hover:shadow-md">
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <Shield className="h-5 w-5 text-primary" />
                          <h3 className="text-lg font-semibold text-foreground">
                            {plan.name}
                          </h3>
                        </div>
                        <p className="mt-1 text-sm text-muted-foreground">
                          {plan.provider}
                        </p>
                      </div>
                    </div>

                    {/* Coverage & Premium */}
                    <div className="flex gap-4">
                      <div className="flex-1 rounded-lg bg-primary/10 p-3">
                        <p className="text-xs text-muted-foreground">Coverage</p>
                        <p className="mt-1 text-lg font-bold text-primary">
                          {plan.coverage}
                        </p>
                      </div>
                      <div className="flex-1 rounded-lg bg-muted p-3">
                        <p className="text-xs text-muted-foreground">Premium</p>
                        <p className="mt-1 text-lg font-bold text-foreground">
                          {plan.premium}
                        </p>
                      </div>
                    </div>

                    {/* Features */}
                    <div>
                      <p className="mb-2 text-sm font-medium text-foreground">
                        Key Features
                      </p>
                      <div className="space-y-1.5">
                        {plan.features.map((feature, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-2 text-sm text-muted-foreground"
                          >
                            <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
                            <span>{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Action */}
                    <Button
                      className="w-full"
                      onClick={() => {
                        toast.success(`Requesting details for ${plan.name}`);
                      }}
                    >
                      Get Quote
                    </Button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Info Card */}
          {!isRecording && (
            <Card className="mt-4 bg-muted/50 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-primary/10 p-2">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">
                    Need Help Choosing?
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Talk to our insurance advisor above. They'll ask about your age, family, health situation, and budget to recommend the perfect plan for you.
                  </p>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}