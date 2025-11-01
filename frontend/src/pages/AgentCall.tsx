import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Phone, PhoneOff, Calendar, Mic, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import { useLocation, useNavigate } from "react-router-dom";

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

  const simulateCall = () => {
    setIsCallActive(true);
    setMessages([]);
    
    const callScript = [
      { speaker: "agent" as const, text: "Hello, I'm calling on behalf of a patient to book an appointment.", delay: 1000 },
      { speaker: "hospital" as const, text: "Good day! How can I help you?", delay: 3000 },
      { speaker: "agent" as const, text: "I'd like to schedule a consultation for general medicine.", delay: 5000 },
      { speaker: "hospital" as const, text: "Sure, let me check our availability. What date works for you?", delay: 7500 },
      { speaker: "agent" as const, text: "Tomorrow afternoon would be ideal if possible.", delay: 10000 },
      { speaker: "hospital" as const, text: "We have slots at 2 PM and 4 PM tomorrow. Which would you prefer?", delay: 12500 },
      { speaker: "agent" as const, text: "2 PM would be perfect.", delay: 15000 },
      { speaker: "hospital" as const, text: "Great! I've booked the appointment for tomorrow at 2 PM. A confirmation will be sent shortly.", delay: 17500 },
      { speaker: "agent" as const, text: "Thank you for your assistance!", delay: 20000 },
    ];

    callScript.forEach((msg) => {
      setTimeout(() => {
        setMessages((prev) => [...prev, { ...msg, timestamp: new Date() }]);
      }, msg.delay);
    });

    setTimeout(() => {
      setIsCallActive(false);
      setCallCompleted(true);
      toast.success("Appointment booked successfully!");
    }, 21000);
  };

  const scheduleGoogleMeet = async () => {
    setIsScheduling(true);
    
    try {
      // In a real implementation, this would use the Google Calendar API
      // For demo purposes, we'll open Google Calendar with pre-filled details
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(14, 0, 0, 0);
      
      const endTime = new Date(tomorrow);
      endTime.setHours(15, 0, 0, 0);
      
      const title = encodeURIComponent(`Appointment at ${hospital?.name || "Hospital"}`);
      const details = encodeURIComponent("Medical consultation booked via PraanLink");
      const location = encodeURIComponent(hospital?.address || "");
      
      const startISO = tomorrow.toISOString().replace(/-|:|\.\d\d\d/g, "");
      const endISO = endTime.toISOString().replace(/-|:|\.\d\d\d/g, "");
      
      const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${startISO}/${endISO}&details=${details}&location=${location}&add=&conf=1`;
      
      window.open(googleCalendarUrl, "_blank");
      
      setTimeout(() => {
        setIsScheduling(false);
        toast.success("Google Meet link created! Calendar event opened.");
      }, 1000);
    } catch (error) {
      console.error("Error scheduling:", error);
      toast.error("Failed to schedule meeting");
      setIsScheduling(false);
    }
  };

  return (
    <div className="flex h-full flex-col items-center justify-center p-6 bg-gradient-to-br from-primary-lighter to-secondary/20">
      <Card className="w-full max-w-3xl p-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-foreground">AI Appointment Agent</h1>
            <p className="mt-2 text-muted-foreground">
              {hospital?.name || "Hospital"} - {hospital?.phone || "Phone"}
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

          {/* Conversation */}
          <Card className="h-80 overflow-y-auto bg-muted/50 p-4">
            {messages.length === 0 ? (
              <div className="flex h-full items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <Mic className="mx-auto h-12 w-12 mb-2" />
                  <p>Start the call to begin booking</p>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.speaker === "agent" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg px-4 py-2 ${
                        msg.speaker === "agent"
                          ? "bg-primary text-primary-foreground"
                          : "bg-card text-card-foreground border border-border"
                      }`}
                    >
                      <p className="text-xs font-semibold mb-1">
                        {msg.speaker === "agent" ? "AI Agent" : hospital?.name || "Hospital"}
                      </p>
                      <p className="text-sm">{msg.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Actions */}
          <div className="flex gap-4">
            {!callCompleted ? (
              <>
                <Button
                  onClick={simulateCall}
                  disabled={isCallActive}
                  className="flex-1"
                  size="lg"
                >
                  <Phone className="mr-2 h-5 w-5" />
                  {isCallActive ? "Call in Progress..." : "Start Call"}
                </Button>
                <Button
                  onClick={() => navigate("/appointments")}
                  variant="outline"
                  size="lg"
                >
                  <PhoneOff className="mr-2 h-5 w-5" />
                  Cancel
                </Button>
              </>
            ) : (
              <>
                <Button
                  onClick={scheduleGoogleMeet}
                  disabled={isScheduling}
                  className="flex-1"
                  size="lg"
                >
                  <Calendar className="mr-2 h-5 w-5" />
                  {isScheduling ? "Scheduling..." : "Add to Google Calendar"}
                </Button>
                <Button
                  onClick={() => navigate("/appointments")}
                  variant="outline"
                  size="lg"
                >
                  Back to Appointments
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
