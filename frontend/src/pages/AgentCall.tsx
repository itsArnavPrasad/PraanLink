import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Phone, PhoneOff, Calendar, Mic, CheckCircle, Square, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

// Import utility classes
import { GeminiLiveAPI } from "@/utils/gemini-live-api";
import { AudioRecorder } from "@/utils/audio-recorder";
import { AudioStreamer } from "@/utils/audio-streamer";
import { SequentialCallRecorder } from "@/utils/sequential-call-recorder";

interface CallMessage {
  speaker: "agent" | "hospital";
  text: string;
  timestamp: Date;
}

export default function AgentCall() {
  const location = useLocation();
  const navigate = useNavigate();
  const hospital = location.state?.hospital;
  
  const [isCallActive, setIsCallActive] = useState(false);
  const [callCompleted, setCallCompleted] = useState(false);
  const [messages, setMessages] = useState<CallMessage[]>([]);
  const [isScheduling, setIsScheduling] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [patientContext, setPatientContext] = useState<string>("");
  const [isLoadingContext, setIsLoadingContext] = useState(true);

  const geminiAPIRef = useRef<any>(null);
  const audioRecorderRef = useRef<any>(null);
  const audioStreamerRef = useRef<any>(null);
  const callRecorderRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const initializedRef = useRef(false);
  
  // Track appointment confirmation details
  const appointmentDetailsRef = useRef<{
    confirmed: boolean;
    date?: string;
    time?: string;
    hospitalEmail?: string;
    doctorName?: string;
    confirmationNumber?: string;
  }>({ confirmed: false });

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

  // Pre-load patient medical context before initializing agent
  useEffect(() => {
    const loadPatientContext = async () => {
      try {
        setIsLoadingContext(true);
        const response = await fetch(`${BACKEND_URL}/appointments/get-patient-context`);
        const data = await response.json();
        
        if (data.success && data.context) {
          setPatientContext(data.context);
          console.log("✅ Patient medical context loaded successfully");
          console.log(data.context)
        } else {
          console.warn("⚠️ Could not load patient context, agent will use tool calls");
          setPatientContext("");
        }
      } catch (error) {
        console.error("❌ Error loading patient context:", error);
        setPatientContext("");
      } finally {
        setIsLoadingContext(false);
      }
    };
    
    loadPatientContext();
  }, []);

  // Initialize Gemini API - waits for patient context to load
  useEffect(() => {
    if (!hospital) {
      toast.error("No hospital information provided");
      return;
    }

    // Wait for patient context to be loaded before initializing agent
    if (isLoadingContext) {
      console.log("⏳ Waiting for patient context to load...");
      return;
    }

    // Get current date and time in multiple formats for the agent
    const now = new Date();
    const currentDateISO = now.toISOString().split('T')[0]; // YYYY-MM-DD
    const currentTimeISO = now.toISOString().split('T')[1].split('.')[0]; // HH:MM:SS
    const currentDateTime = now.toISOString(); // Full ISO datetime
    const currentDateFormatted = now.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
    const currentTimeFormatted = now.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      timeZoneName: 'short'
    });

    // Build system instruction with pre-loaded patient context
    const patientContextSection = patientContext 
      ? `\n\n=== PATIENT MEDICAL CONTEXT (PRE-LOADED) ===\nYou have been provided with the complete patient medical profile. Use this information to explain why the appointment is needed:\n\n${patientContext}\n\n=== END OF PATIENT CONTEXT ===\n\nIMPORTANT: You already have all the patient's medical information above. You do NOT need to call getMedicalHistory tool - the data is already provided here. Use this context directly when talking to the hospital.`
      : `\n\nNOTE: If you need specific medical information during the conversation, you can use the getMedicalHistory tool, but try to use the context provided in this instruction first.`;

    const systemInstruction = `You are a professional AI assistant calling a hospital on behalf of a patient to book a medical appointment. You are speaking directly to hospital staff.

CURRENT DATE AND TIME REFERENCE:
- Today's Date: ${currentDateFormatted}
- Current Date (ISO): ${currentDateISO}
- Current Time: ${currentTimeFormatted}
- Full Current DateTime (ISO): ${currentDateTime}
- Use this information when discussing appointment dates and times
- When hospital mentions dates, calculate relative to today: ${currentDateISO}

YOUR ROLE AND IDENTITY:
- You are calling ${hospital.name} at ${hospital.phone} on behalf of a patient
- When you speak, you represent the patient - use "I" when referring to the patient's needs
- Example: "I'd like to schedule an appointment" (meaning the patient wants to schedule)
- You are polite, professional, and efficient
- You have access to the patient's complete medical history

CALL OBJECTIVE:
Your primary goal is to successfully book a medical appointment by:
1. Understanding the patient's medical needs from their history
2. Explaining to the hospital why an appointment is needed
3. Finding the most suitable appointment time
4. Confirming all appointment details
5. Creating a calendar event once confirmed

HOW TO HANDLE THE CONVERSATION (Natural Flow):

1. START THE CALL NATURALLY (You already have patient medical data):
   - Introduce yourself when you begin speaking
   - Explain you're calling on behalf of a patient
   - Use the patient medical context provided above to explain why the appointment is needed
   - Be specific about symptoms, concerns, lab results, or follow-up requirements from the patient data
   - Let the conversation flow naturally based on what the hospital staff says

2. EXPLAIN APPOINTMENT NEED:
   - Use the patient medical context provided above (symptoms, medications, lab results, risk factors, conditions)
   - Be specific and reference actual patient data when explaining appointment needs
   - Adjust your explanation based on the staff's responses

3. BOOK THE APPOINTMENT:
   - Have a natural conversation about available times
   - Be flexible and work with what they offer
   - Respond naturally to their questions and suggestions

4. CONFIRM DETAILS:
   - Make sure you understand all appointment details correctly
   - Ask clarifying questions if needed
   - Repeat back important information to confirm

5. SEND DOCUMENTS IF REQUESTED:
   - If they ask for medical reports, use sendEmail tool
   - Only send what they specifically request

6. DURING APPOINTMENT CONFIRMATION (CRITICAL - MANDATORY):
   - When the hospital confirms the appointment, you MUST:
     1. Extract and confirm these details:
        - Confirmed date and time
        - Hospital email address (MANDATORY - you MUST ask for this if not provided, say: "Could I please get your email address so I can send the medical report?")
        - Doctor name (if mentioned)
        - Confirmation number (if provided)
     
     2. ASK FOR CONFIRMATION before sending email:
        - Say: "Perfect! Before I end the call, I'd like to confirm: should I send the medical report PDF to your email?"
        - Wait for their confirmation (they may say "yes", "go ahead", "please do", etc.)
     
     3. AFTER RECEIVING CONFIRMATION, call sendEmail tool:
        - Use the hospital email address you obtained
        - Subject: "Medical Report for Appointment - [Hospital Name]"
        - Body: Include appointment confirmation details (date, time, patient info)
        - The system will automatically attach PraanLink_Medical_Report.pdf
     
     4. AFTER THE EMAIL HAS BEEN SUCCESSFULLY SENT:
        - Confirm the action is done: "Great! I've sent the medical report PDF to your email."
        - Then say: "Everything is confirmed and set up. I'm ending the call now. Thank you for your help!"
        - The call will end after this
   
   - IMPORTANT: You MUST call sendEmail tool during the conversation (not automatically)
   - DO NOT end the call until the email has been successfully sent
   - If the email fails, inform the hospital and try to resolve the issue before ending

LIVE CONVERSATION GUIDELINES:
- This is a REAL, LIVE conversation - respond naturally to whatever is said
- Listen carefully to what the hospital staff tells you and respond appropriately
- Adapt your approach based on their responses - don't stick to a script
- If they ask a question, answer it naturally based on the context
- If they suggest something, respond to it in real-time
- Be conversational and human-like in your responses
- Think on your feet and handle unexpected situations naturally
- Use "I" when speaking on behalf of the patient naturally
- Show appreciation and be polite, but keep it natural, not scripted

HOSPITAL INFORMATION:
- Hospital Name: ${hospital.name}
- Address: ${hospital.address}
- Phone: ${hospital.phone}
- Specialties: ${hospital.specialties?.join(", ") || "General Medicine"}

CRITICAL REMINDERS:
- You already have the patient's complete medical context provided above - use it directly, no need to call getMedicalHistory tool
- IMPORTANT: When appointment is confirmed, you MUST:
  1. Ask for confirmation to send email
  2. Call sendEmail tool (during the conversation)
  3. Confirm the action completed successfully
  4. Announce you're ending the call
  5. Only then should the call end
- Remember to ask for hospital email address when confirming appointment
- Be thorough in confirming all appointment details (date, time, location, doctor, email) before asking for final confirmation
- If the hospital staff sounds busy or rushed, be brief but complete
- Reference specific patient data from the context above when explaining appointment needs
- DO NOT end the call until you have successfully called sendEmail tool

CONVERSATION BEHAVIOR:
- This is a LIVE, REAL-TIME conversation - no scripted responses
- You are having a natural, flowing conversation with hospital staff
- Respond naturally to what they say in real-time
- Adapt your responses based on their actual replies
- Be flexible and handle the conversation as it unfolds
- Think on your feet and respond contextually to each interaction

BEGINNING THE CALL:
- You already have the complete patient medical profile loaded in your context (see PATIENT MEDICAL CONTEXT section above)
- Start by introducing yourself naturally and immediately explain the appointment need using the patient data from your context
- Reference specific symptoms, conditions, lab results, or risk factors from the patient context
- Let the conversation flow naturally - listen to what the hospital staff says and respond accordingly
- Use specific information from the patient context when explaining why the appointment is needed
- Do NOT use any pre-written scripts or hardcoded responses - use the actual patient medical data from your context
- If you need additional specific information not in your context, you can optionally use getMedicalHistory tool, but you should have everything you need already

The person you're talking to is the hospital front desk staff. This is a real, live phone call conversation powered by Gemini Live API with real-time audio.${patientContextSection}`;

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
              voice_name: "Charon" // Professional voice for business calls
            }
          }
        }
      },
      tools: [
        {
          functionDeclarations: [
            {
              name: "getMedicalHistory",
              description: "OPTIONAL RAG TOOL: Access additional patient medical information if needed. You already have the patient's complete medical context pre-loaded in your system instruction, so you typically don't need to call this tool. Only use this if you need to search for very specific information that wasn't included in your pre-loaded context or if you need to refresh/update the medical data during the conversation.",
              parameters: {
                type: "object",
                properties: {
                  query: {
                    type: "string",
                    description: "Natural language query for specific information. Examples: 'specific symptom details', 'detailed lab values', 'medication dosages', etc. Use only if you need information not already in your context.",
                  },
                },
                required: ["query"],
              },
            },
            {
              name: "sendEmail",
              description: "MANDATORY: Send the patient's medical report PDF to the hospital email. You MUST call this tool AFTER the hospital confirms they want the medical report sent. Call this AFTER asking for confirmation and BEFORE ending the call. The system will automatically attach PraanLink_Medical_Report.pdf. Include appointment confirmation details in the email body.",
              parameters: {
                type: "object",
                properties: {
                  to: {
                    type: "string",
                    description: "Hospital email address (ask the hospital staff for their email if not provided)",
                  },
                  subject: {
                    type: "string",
                    description: "Email subject line (e.g., 'Medical Report for Appointment - [Patient Name]')",
                  },
                  body: {
                    type: "string",
                    description: "Email body with appointment confirmation details, patient information, and appointment date/time",
                  },
                  attachments: {
                    type: "array",
                    items: {
                      type: "string"
                    },
                    description: "Leave empty or pass ['PraanLink_Medical_Report.pdf'] - the system will automatically attach the medical report PDF",
                  },
                },
                required: ["to", "subject", "body"],
              },
            },
          ],
        },
      ],
    };

    geminiAPIRef.current = new GeminiLiveAPI(endpoint, true, customSetupConfig);

    geminiAPIRef.current.onSetupComplete = () => {
      console.log('Gemini API setup complete - live conversation ready');
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
      console.log("🔧 Tool call received (raw):", JSON.stringify(toolCall, null, 2));
      
      // Handle different tool call formats
      // Format 1: {functionCalls: [{name, args, id}]}
      // Format 2: {name, arguments, call_id}
      let functionCalls: any[] = [];
      if (toolCall.functionCalls && Array.isArray(toolCall.functionCalls)) {
        console.log("📋 Detected functionCalls array format");
        functionCalls = toolCall.functionCalls;
      } else if (toolCall.name) {
        console.log("📋 Detected direct name format");
        // Single tool call in old format
        functionCalls = [{
          name: toolCall.name,
          args: toolCall.arguments || toolCall.args,
          id: toolCall.call_id || toolCall.id
        }];
      } else {
        console.error("❌ Unknown tool call format:", toolCall);
        return;
      }
      
      console.log(`📋 Processing ${functionCalls.length} function call(s)`);
      
      // Process each function call
      for (const funcCall of functionCalls) {
        const toolName = funcCall.name;
        const toolArgs = funcCall.args || funcCall.arguments || {};
        const callId = funcCall.id || funcCall.call_id;
        
        console.log(`🔧 Processing tool call: ${toolName}`, { 
          args: toolArgs, 
          callId,
          fullFunctionCall: funcCall
        });
        
        if (toolName === "getMedicalHistory") {
          // Optional tool - agent should already have context, but can use for specific queries
          const query = toolArgs.query;
          
          try {
            console.log(`🔍 Optional RAG Tool: Querying additional medical data with: "${query}"`);
            
            const response = await fetch(`${BACKEND_URL}/appointments/get-medical-history`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ query }),
            });
        
            const data = await response.json();
            
            if (data.success && data.data) {
              const medicalInfo = typeof data.data === 'string' ? data.data : JSON.stringify(data.data, null, 2);
              console.log(`✅ RAG Tool: Retrieved additional information (${medicalInfo.length} chars)`);
              
              // Don't send tool result - agent already has context from system instructions
              console.log("⚠️ RAG tool result not sent - agent has pre-loaded context");
            } else {
              console.log("⚠️ No additional medical information found - agent has pre-loaded context");
            }
          } catch (error) {
            console.error('❌ Medical history RAG error:', error);
            // Don't send tool result - agent has pre-loaded context
          }
        } else if (toolName === "sendEmail") {
          const { to, subject, body, attachments } = toolArgs;
          
          try {
            // Always attach the medical report PDF - backend will find it automatically
            const medicalReportPath = "PraanLink_Medical_Report.pdf";
            const attachmentList = attachments && attachments.length > 0 
              ? attachments 
              : [medicalReportPath];
            
            // Ensure medical report is included
            if (!attachmentList.includes(medicalReportPath)) {
              attachmentList.push(medicalReportPath);
            }
            
            console.log(`📧 Sending email with medical report PDF to: ${to}`);
            
            const response = await fetch(`${BACKEND_URL}/appointments/send-email`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ 
                to, 
                subject, 
                body, 
                attachments: attachmentList 
              }),
            });
        
            const data = await response.json();
        
            if (data.success) {
              console.log(`✅ Email sent successfully with PDF attachment`);
              // Don't send tool result to avoid WebSocket closure
              // Instead, wait a moment and let agent continue naturally
              toast.success(`✅ Email sent to ${data.to}`);
              
              // Track hospital email
              if (!appointmentDetailsRef.current.hospitalEmail && data.to) {
                appointmentDetailsRef.current.hospitalEmail = data.to;
                console.log(`📧 Hospital email captured: ${data.to}`);
              }
              
              // The agent will continue based on its system instructions
              // It will end the call after confirming email was sent
            } else {
              console.error(`❌ Email failed: ${data.error}`);
              toast.error(`Failed to send email: ${data.error || "Unknown error"}`);
            }
          } catch (error) {
            console.error('❌ Email error:', error);
            toast.error("Unable to send email at this time. Please try again.");
          }
        } else {
          console.warn(`⚠️ Unknown tool name: ${toolName}`);
        }
      } // End of for loop
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
  }, [hospital, patientContext, isLoadingContext]); // Re-initialize when context loads

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

  const handleStartCall = async () => {
    if (!hospital) {
      toast.error("No hospital information available");
      return;
    }

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
        // Only send audio if WebSocket is open
        if (geminiAPIRef.current?.ws?.readyState === WebSocket.OPEN) {
          geminiAPIRef.current?.sendAudioChunk(base64Data);
        } else {
          console.warn("⚠️ WebSocket not open, skipping audio chunk. State:", geminiAPIRef.current?.ws?.readyState);
        }
      });

      callRecorderRef.current = new SequentialCallRecorder(24000);
      
      const userStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      await callRecorderRef.current.startRecording(userStream);

      setIsCallActive(true);
      setIsRecording(true);
      setElapsed(0);
      setCallCompleted(false);
      setMessages([]);
      
      // Reset appointment details when starting a new call
      appointmentDetailsRef.current = { confirmed: false };
      console.log("🔄 Reset appointment details for new call");
      
      toast.success("Call started - Live conversation ready");

      // Trigger the agent to start the live conversation
      // Agent already has patient context pre-loaded, so it can start immediately
      const startLiveConversation = () => {
        if (geminiAPIRef.current?.ws.readyState === WebSocket.OPEN) {
          // Agent already has all patient medical data in context, so start the call immediately
          // No need to wait for tool calls - use the pre-loaded patient context
          geminiAPIRef.current.sendTextMessage("Start the call now. You already have the patient's complete medical profile in your context. Introduce yourself to the hospital staff and explain the appointment need using the patient medical data you have.");
        } else {
          // Wait for WebSocket to be ready
          setTimeout(startLiveConversation, 200);
        }
      };
      
      // Small delay to ensure everything is initialized, then start live conversation
      setTimeout(startLiveConversation, 1500);

    } catch (error: any) {
      console.error('Error starting call:', error);
      toast.error('Error starting call: ' + error.message);
    }
  };

  const handleEndCall = async () => {
    setIsProcessing(true);
    
    try {
      if (audioRecorderRef.current) {
        audioRecorderRef.current.stop();
        audioRecorderRef.current.off('data');
      }

      if (callRecorderRef.current && callRecorderRef.current.isCurrentlyRecording()) {
        await callRecorderRef.current.stopRecording();
      }

      geminiAPIRef.current?.sendEndMessage();

      setIsRecording(false);
      setIsCallActive(false);
      
      // Note: Since the agent now calls sendEmail during the conversation,
      // we don't need to auto-process when the call ends
      // The email has already been sent during the conversation
      console.log("📋 Call ended. Checking if appointment was confirmed...");
      const appointmentDetails = appointmentDetailsRef.current;
      
      if (appointmentDetails.confirmed && appointmentDetails.hospitalEmail) {
        console.log("✅ Appointment was confirmed and email was sent during conversation");
        toast.success("Call completed successfully");
      } else {
        console.log("ℹ️ No appointment was confirmed during this call");
        toast.info("Call ended");
      }
      
    } catch (error: any) {
      console.error('Error ending call:', error);
      toast.error('Error ending call: ' + error.message);
    } finally {
      setIsProcessing(false);
      // Don't reset appointment details here - let them persist for debugging
      // They'll be reset when a new call starts
    }
  };


  if (!hospital) {
    return (
      <div className="flex h-full items-center justify-center">
        <Card className="p-8">
          <p className="text-lg text-muted-foreground">No hospital information provided</p>
          <Button onClick={() => navigate("/appointments")} className="mt-4">
            Back to Appointments
          </Button>
        </Card>
      </div>
    );
  }

  if (isLoadingContext) {
    return (
      <div className="flex h-full items-center justify-center">
        <Card className="p-8">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-lg font-medium">Loading patient medical context...</p>
            <p className="text-sm text-muted-foreground">Preparing agent with your medical data</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col items-center justify-center p-6 bg-gradient-to-br from-primary-lighter to-secondary/20">
      <Card className="w-full max-w-3xl p-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-foreground">AI Appointment Agent</h1>
            <p className="mt-2 text-muted-foreground">
              {hospital.name} - {hospital.phone}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {hospital.address}
            </p>
          </div>

          {/* Call Status */}
          <div className="flex items-center justify-center">
            <div className={`relative flex h-32 w-32 items-center justify-center rounded-full ${
              isCallActive ? "bg-primary animate-pulse" : callCompleted ? "bg-green-500" : "bg-muted"
            }`}>
              {callCompleted ? (
                <CheckCircle className="h-16 w-16 text-white" />
              ) : isCallActive ? (
                <>
                  <Phone className="h-16 w-16 text-primary-foreground" />
                  <div className="absolute h-full w-full animate-ping rounded-full bg-primary opacity-75"></div>
                </>
              ) : (
                <Phone className="h-16 w-16 text-muted-foreground" />
              )}
            </div>
          </div>

          {/* Timer Display */}
          {isRecording && (
                <div className="text-center">
              <div className="text-2xl font-bold">{formatTime(elapsed)}</div>
                </div>
          )}

          {/* Audio Visualizer */}
          <AnimatePresence>
            {isRecording && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex justify-center gap-1 h-16 items-end"
              >
                {[...Array(15)].map((_, i) => (
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
                    className="w-2 bg-gradient-to-t from-primary to-secondary rounded-full"
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Status Messages */}
          <div className="text-center">
            {isProcessing ? (
              <p className="text-lg text-muted-foreground">Processing...</p>
            ) : isCallActive ? (
              <p className="text-lg font-medium text-foreground">
                {isAISpeaking && (
                  <motion.span
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    className="block mt-2 text-primary"
                  >
                    AI Agent is speaking...
                  </motion.span>
                )}
                Call in progress - AI agent is talking to hospital staff
              </p>
            ) : callCompleted ? (
              <p className="text-lg font-medium text-green-600">
                Appointment booked successfully!
              </p>
            ) : (
              <p className="text-lg text-muted-foreground">
                Ready to start the call
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            {!callCompleted ? (
              <>
                <Button
                  onClick={isCallActive ? handleEndCall : handleStartCall}
                  disabled={isProcessing}
                  className="flex-1"
                  size="lg"
                  variant={isCallActive ? "destructive" : "default"}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      Processing...
                    </>
                  ) : isCallActive ? (
                    <>
                      <PhoneOff className="mr-2 h-5 w-5" />
                      End Call
                    </>
                  ) : (
                    <>
                  <Phone className="mr-2 h-5 w-5" />
                      Start Call
                    </>
                  )}
                </Button>
                <Button
                  onClick={() => navigate("/appointments")}
                  variant="outline"
                  size="lg"
                >
                  Cancel
                </Button>
              </>
            ) : (
                <Button
                onClick={() => navigate("/appointments")}
                  className="flex-1"
                  size="lg"
                >
                  Back to Appointments
                </Button>
            )}
          </div>

          {/* Info Card */}
          {!isCallActive && !callCompleted && (
            <Card className="p-6 bg-muted/50">
              <h3 className="mb-3 text-lg font-semibold text-foreground">
                What the AI Agent Will Do
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Review your medical history (check-ins, prescriptions, reports)</li>
                <li>• Call the hospital on your behalf</li>
                <li>• Discuss your medical needs and find the best appointment time</li>
                <li>• Send medical reports via email once appointment is confirmed</li>
              </ul>
            </Card>
          )}
        </div>
      </Card>
    </div>
  );
}