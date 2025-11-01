import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Mic, MicOff, CheckCircle2, Shield, Users } from "lucide-react";
import { toast } from "sonner";

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

interface Message {
  id: number;
  type: "user" | "assistant";
  content: string;
}

export default function Insurance() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: "assistant",
      content:
        "Hello! I'm your insurance advisor. I can help you find the perfect health insurance plan based on your needs. What would you like to know?",
    },
  ]);
  const [isRecording, setIsRecording] = useState(false);
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);

  const mockConversations = [
    {
      user: "I'm looking for health insurance for my family.",
      assistant: "Great! I'd recommend our Comprehensive Health Plus plan. It offers ₹10 Lakh coverage with cashless hospitalization and covers the entire family.",
    },
    {
      user: "What about pre-existing conditions?",
      assistant: "All plans cover pre-existing diseases after a waiting period. The Star Health plan has the shortest waiting period of 2 years.",
    },
    {
      user: "How much would the premium be?",
      assistant: "For a family of four, the Comprehensive Health Plus would be approximately ₹15,000 per year. You can see all details on the right.",
    },
    {
      user: "Can I add more family members later?",
      assistant: "Yes! You can add family members during the policy renewal period, and the premium will be adjusted accordingly.",
    },
  ];

  const startRecording = () => {
    setIsRecording(true);
    toast.info("Listening...");

    // Simulate recording for 2-3 seconds
    setTimeout(() => {
      setIsRecording(false);
      
      // Pick a random conversation
      const conversation = mockConversations[Math.floor(Math.random() * mockConversations.length)];
      
      // Add user message
      const userMessage: Message = {
        id: messages.length + 1,
        type: "user",
        content: conversation.user,
      };
      setMessages((prev) => [...prev, userMessage]);

      // Agent responds after a delay
      setTimeout(() => {
        setIsAgentSpeaking(true);
        
        setTimeout(() => {
          const assistantMessage: Message = {
            id: messages.length + 2,
            type: "assistant",
            content: conversation.assistant,
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setIsAgentSpeaking(false);
        }, 1500);
      }, 1000);
    }, 2500);
  };

  return (
    <div className="flex h-full flex-col lg:flex-row">
      {/* Left Side - Chat Assistant */}
      <div className="flex w-full flex-col border-b border-border lg:h-full lg:w-1/2 lg:border-b-0 lg:border-r">
        {/* Header */}
        <div className="border-b border-border bg-card px-6 py-5">
          <h2 className="text-xl font-bold text-foreground">
            Insurance Assistant
          </h2>
          <p className="text-sm text-muted-foreground">
            Ask me anything about health insurance
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-4 overflow-auto p-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.type === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
            </div>
          ))}
          
          {/* Agent Speaking Indicator */}
          {isAgentSpeaking && (
            <div className="flex justify-start">
              <div className="bg-muted text-foreground rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <span className="animate-bounce" style={{ animationDelay: "0ms" }}>●</span>
                    <span className="animate-bounce" style={{ animationDelay: "150ms" }}>●</span>
                    <span className="animate-bounce" style={{ animationDelay: "300ms" }}>●</span>
                  </div>
                  <span className="text-sm">Agent is speaking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Voice Controls */}
        <div className="border-t border-border bg-card p-6">
          <div className="flex flex-col items-center gap-4">
            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                {isRecording ? "Listening to your question..." : "Tap to speak with the insurance advisor"}
              </p>
            </div>
            
            <Button
              onClick={startRecording}
              disabled={isRecording || isAgentSpeaking}
              size="lg"
              className={`h-20 w-20 rounded-full ${
                isRecording ? "animate-pulse" : ""
              }`}
            >
              {isRecording ? (
                <MicOff className="h-8 w-8" />
              ) : (
                <Mic className="h-8 w-8" />
              )}
            </Button>
            
            {isRecording && (
              <div className="flex gap-1">
                <div className="h-8 w-1 bg-primary animate-pulse" style={{ animationDelay: "0ms" }}></div>
                <div className="h-8 w-1 bg-primary animate-pulse" style={{ animationDelay: "100ms" }}></div>
                <div className="h-8 w-1 bg-primary animate-pulse" style={{ animationDelay: "200ms" }}></div>
                <div className="h-8 w-1 bg-primary animate-pulse" style={{ animationDelay: "300ms" }}></div>
                <div className="h-8 w-1 bg-primary animate-pulse" style={{ animationDelay: "400ms" }}></div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right Side - Insurance Plans */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <div className="border-b border-border bg-card px-6 py-5">
          <h2 className="text-xl font-bold text-foreground">
            Recommended Plans
          </h2>
          <p className="text-sm text-muted-foreground">
            Personalized for your health profile
          </p>
        </div>

        {/* Plans List */}
        <div className="flex-1 overflow-auto p-6">
          <div className="space-y-4">
            {insurancePlans.map((plan) => (
              <Card
                key={plan.id}
                className="p-5 transition-smooth hover:shadow-md"
              >
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
            ))}
          </div>

          {/* Info Card */}
          <Card className="mt-4 bg-muted/50 p-4">
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-primary-lighter p-2">
                <Users className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">
                  Family Coverage Available
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Add family members to these plans for better rates and comprehensive coverage
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
