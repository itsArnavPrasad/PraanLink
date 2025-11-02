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
  const [recommendedPlans, setRecommendedPlans] = useState<InsurancePlan[]>(insurancePlans);

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
- You are an expert insurance consultant who understands health insurance products, coverage options, and user needs
- You help users navigate the complex world of health insurance with patience and clarity
- You analyze user's health profile, family situation, and financial considerations to recommend the best plans
- You have access to a comprehensive database of insurance plans and can search through them

CONVERSATION STYLE:
- Speak naturally and conversationally in English
- Be warm, professional, and trustworthy
- Ask thoughtful questions to understand their needs fully
- Explain insurance terms in simple language when needed
- Show genuine interest in finding the right coverage for them
- Be transparent about costs, coverage, and limitations

KEY AREAS TO EXPLORE:
1. Personal Information:
   - Age and health status of user and family members
   - Pre-existing conditions or ongoing treatments
   - Family size and ages of dependents
   
2. Coverage Needs:
   - Expected medical expenses and hospitalization needs
   - Preferred coverage amount
   - Important features (cashless, room rent, pre-post hospitalization, etc.)
   
3. Financial Considerations:
   - Budget for premium payments
   - Preferred payment frequency (monthly/quarterly/yearly)
   
4. Specific Requirements:
   - Network hospitals preference
   - Maternity coverage needs
   - Critical illness coverage
   - Wellness benefits

IMPORTANT GUIDELINES:
- Start by warmly greeting the user and introducing yourself as their insurance advisor
- Ask about their current insurance status (if any)
- Gather information about their health profile and family situation
- Use searchInsurancePlans to find plans that match their requirements
- Use searchUserHealth to understand their medical history and current health conditions
- Use searchUserReports to review their medical reports and prescriptions
- Provide personalized recommendations with clear explanations
- Compare plans when asked and explain trade-offs
- Guide them through the decision-making process step by step
- Always be honest about what's covered and what's not
- Never pressure them - let them make informed decisions

TOOL USAGE:
- Use searchInsurancePlans when you need to find specific plans based on coverage, premium, features, or providers
- Use searchUserHealth when you need context about their medical history, check-in summaries, or health conditions
- Use searchUserReports when you need to review their prescriptions, medical reports, or treatment history
- Combine information from all tools to provide the most personalized recommendations

Begin by warmly introducing yourself and asking the user about their insurance needs and current situation.`;

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
              voice_name: "Charon" // Professional, trustworthy voice
            }
          }
        }
      },
      tools: [
        {
          functionDeclarations: [
            {
              name: "searchInsurancePlans",
              description: "Search the insurance database for plans that match specific criteria. Use this to find plans based on coverage amount, premium range, specific features, provider, or any combination of requirements.",
              parameters: {
                type: "object",
                properties: {
                  query: {
                    type: "string",
                    description: "The search query describing the insurance requirements (e.g., 'family plan under 20000 with maternity coverage', 'individual plan 5 lakh coverage', 'plans with pre-existing disease coverage')",
                  },
                  minCoverage: {
                    type: "number",
                    description: "Minimum coverage amount in lakhs (optional)",
                  },
                  maxPremium: {
                    type: "number",
                    description: "Maximum annual premium amount in rupees (optional)",
                  },
                },
                required: ["query"],
              },
            },
            {
              name: "searchUserHealth",
              description: "Search the user's health history including past check-in summaries, diagnosed conditions, symptoms, medications, and overall health status. Use this to understand their medical profile.",
              parameters: {
                type: "object",
                properties: {
                  query: {
                    type: "string",
                    description: "What to search for in the user's health history (e.g., 'pre-existing conditions', 'current medications', 'recent health check-ins', 'chronic conditions')",
                  },
                },
                required: ["query"],
              },
            },
            {
              name: "searchUserReports",
              description: "Search the user's medical reports, prescriptions, test results, and treatment history. Use this to get detailed medical information.",
              parameters: {
                type: "object",
                properties: {
                  query: {
                    type: "string",
                    description: "What to search for in medical reports (e.g., 'recent prescriptions', 'blood test results', 'specialist reports', 'ongoing treatments')",
                  },
                },
                required: ["query"],
              },
            },
            {
              name: "updateRecommendedPlans",
              description: "Update the displayed insurance plans on the screen with specific recommendations. Use this after analyzing user needs to show them the most suitable plans.",
              parameters: {
                type: "object",
                properties: {
                  planIds: {
                    type: "array",
                    items: { type: "number" },
                    description: "Array of plan IDs to display as recommendations",
                  },
                  reason: {
                    type: "string",
                    description: "Brief explanation of why these plans are recommended",
                  },
                },
                required: ["planIds", "reason"],
              },
            },
          ],
        },
      ],
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

    geminiAPIRef.current.onToolCall = async (toolCall: any) => {
      console.log("Tool call received:", toolCall);
    
      if (toolCall.name === "searchInsurancePlans") {
        const { query, minCoverage, maxPremium } = toolCall.arguments;
        
        try {
          const response = await fetch(`${BACKEND_URL}/insurance-search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, minCoverage, maxPremium }),
          });
      
          const data = await response.json();
      
          geminiAPIRef.current.sendToolResult(toolCall.call_id, {
            result: data.plans || "No insurance plans found matching these criteria.",
          });
        } catch (error) {
          console.error('Insurance search error:', error);
          geminiAPIRef.current.sendToolResult(toolCall.call_id, {
            result: "Unable to search insurance plans at this time.",
          });
        }
      } else if (toolCall.name === "searchUserHealth") {
        const query = toolCall.arguments.query;
        
        try {
          const response = await fetch(`${BACKEND_URL}/user-health-search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
          });
      
          const data = await response.json();
      
          geminiAPIRef.current.sendToolResult(toolCall.call_id, {
            result: data.answer || "No health information found.",
          });
        } catch (error) {
          console.error('User health search error:', error);
          geminiAPIRef.current.sendToolResult(toolCall.call_id, {
            result: "Unable to search health information at this time.",
          });
        }
      } else if (toolCall.name === "searchUserReports") {
        const query = toolCall.arguments.query;
        
        try {
          const response = await fetch(`${BACKEND_URL}/user-reports-search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
          });
      
          const data = await response.json();
      
          geminiAPIRef.current.sendToolResult(toolCall.call_id, {
            result: data.answer || "No medical reports found.",
          });
        } catch (error) {
          console.error('User reports search error:', error);
          geminiAPIRef.current.sendToolResult(toolCall.call_id, {
            result: "Unable to search medical reports at this time.",
          });
        }
      } else if (toolCall.name === "updateRecommendedPlans") {
        const { planIds, reason } = toolCall.arguments;
        
        // Update the displayed plans based on AI recommendation
        const updatedPlans = insurancePlans.filter(plan => planIds.includes(plan.id));
        setRecommendedPlans(updatedPlans);
        
        toast.success(`Plans updated: ${reason}`);
        
        geminiAPIRef.current.sendToolResult(toolCall.call_id, {
          result: `Successfully updated display with ${updatedPlans.length} recommended plans.`,
        });
      }
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
        
        // Upload recording to backend
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
            {isRecording ? "Analyzing Your Needs..." : "Recommended Plans"}
          </h2>
          <p className="text-sm text-muted-foreground">
            {isRecording 
              ? "Plans will update based on our conversation"
              : "Personalized for your health profile"}
          </p>
        </div>

        {/* Plans List */}
        <div className="flex-1 overflow-auto p-6">
          <AnimatePresence mode="popLayout">
            <div className="space-y-4">
              {recommendedPlans.map((plan) => (
                <motion.div
                  key={plan.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
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
                        <Badge className="bg-primary">
                          {plan.match}% Match
                        </Badge>
                      </div>

                      {/* Coverage & Premium */}
                      <div className="flex gap-4">
                        <div className="flex-1 rounded-lg bg-primary-lighter p-3">
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
          </AnimatePresence>

          {/* Info Card */}
          {!isRecording && (
            <Card className="mt-4 bg-muted/50 p-4">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-primary-lighter p-2">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">
                    Need Help Choosing?
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Talk to our insurance advisor above. They'll analyze your health profile, family needs, and budget to recommend the perfect plan for you.
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