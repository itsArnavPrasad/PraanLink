import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, TrendingUp, AlertCircle, Heart, Moon, Zap, Pill, ActivitySquare } from "lucide-react";
import { toast } from "sonner";

interface CheckInSummary {
  id: number;
  timestamp: string;
  summary: string;
  mood: string;
  symptoms: string[];
  medications_taken: string[];
  sleep_quality: string;
  energy_level: string;
  concerns: string[];
  ai_insights: string[];
  overall_score: string;
}

export default function Summaries() {
  const [checkIns, setCheckIns] = useState<CheckInSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const BACKEND_URL = 'http://localhost:8000';

  useEffect(() => {
    fetchCheckIns();
  }, []);

  const fetchCheckIns = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/checkins/summaries?limit=20`);
      const data = await response.json();
      
      if (data.success) {
        setCheckIns(data.checkins);
      } else {
        toast.error("Failed to load check-ins");
      }
    } catch (error) {
      console.error("Error fetching check-ins:", error);
      toast.error("Error loading check-ins");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getMoodColor = (mood: string) => {
    const moodLower = mood?.toLowerCase() || '';
    if (moodLower.includes('great') || moodLower.includes('excellent') || moodLower.includes('happy')) {
      return 'default';
    } else if (moodLower.includes('okay') || moodLower.includes('neutral') || moodLower.includes('fair')) {
      return 'secondary';
    } else if (moodLower.includes('tired') || moodLower.includes('stressed') || moodLower.includes('anxious')) {
      return 'destructive';
    }
    return 'outline';
  };

  const getScoreColor = (score: string) => {
    const scoreNum = parseInt(score);
    if (scoreNum >= 80) return 'text-green-500';
    if (scoreNum >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (loading) {
    return (
      <div className="flex h-full flex-col">
        <div className="border-b border-border bg-card px-8 py-6">
          <h1 className="text-3xl font-bold text-foreground">Health Summaries</h1>
          <p className="mt-2 text-muted-foreground">
            Your check-in history and health insights
          </p>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading your health summaries...</p>
          </div>
        </div>
      </div>
    );
  }

  if (checkIns.length === 0) {
    return (
      <div className="flex h-full flex-col">
        <div className="border-b border-border bg-card px-8 py-6">
          <h1 className="text-3xl font-bold text-foreground">Health Summaries</h1>
          <p className="mt-2 text-muted-foreground">
            Your check-in history and health insights
          </p>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Calendar className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Check-Ins Yet</h3>
            <p className="text-muted-foreground">
              Start your first daily check-in to see summaries here
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-8 py-6">
        <h1 className="text-3xl font-bold text-foreground">Health Summaries</h1>
        <p className="mt-2 text-muted-foreground">
          Your check-in history and health insights ({checkIns.length} check-ins)
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">
        <div className="mx-auto max-w-5xl space-y-6">
          {checkIns.map((checkIn) => (
            <Card key={checkIn.id} className="p-6 transition-smooth hover:shadow-md">
              {/* Header */}
              <div className="mb-4 flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-primary" />
                    <h3 className="text-lg font-semibold text-foreground">
                      {formatDate(checkIn.timestamp)}
                    </h3>
                  </div>
                  {checkIn.overall_score && (
                    <p className={`mt-1 text-sm font-medium ${getScoreColor(checkIn.overall_score)}`}>
                      Health Score: {checkIn.overall_score}
                    </p>
                  )}
                </div>
                {checkIn.mood && (
                  <Badge variant={getMoodColor(checkIn.mood)} className="capitalize">
                    Mood: {checkIn.mood}
                  </Badge>
                )}
              </div>

              {/* Summary */}
              {checkIn.summary && (
                <div className="mb-4 rounded-lg bg-muted/50 p-4">
                  <p className="text-sm text-foreground leading-relaxed">
                    {checkIn.summary}
                  </p>
                </div>
              )}

              {/* Health Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {/* Sleep Quality */}
                {checkIn.sleep_quality && (
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-500/10">
                    <Moon className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-foreground">Sleep Quality</p>
                      <p className="text-sm text-muted-foreground">{checkIn.sleep_quality}</p>
                    </div>
                  </div>
                )}

                {/* Energy Level */}
                {checkIn.energy_level && (
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-yellow-500/10">
                    <Zap className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-foreground">Energy Level</p>
                      <p className="text-sm text-muted-foreground">{checkIn.energy_level}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Symptoms */}
              {checkIn.symptoms && checkIn.symptoms.length > 0 && (
                <div className="mb-4">
                  <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                    <ActivitySquare className="h-4 w-4 text-red-500" />
                    Symptoms Reported
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {checkIn.symptoms.map((symptom, idx) => (
                      <Badge key={idx} variant="outline" className="bg-red-500/10">
                        {symptom}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Medications */}
              {checkIn.medications_taken && checkIn.medications_taken.length > 0 && (
                <div className="mb-4">
                  <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                    <Pill className="h-4 w-4 text-green-500" />
                    Medications Taken
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {checkIn.medications_taken.map((med, idx) => (
                      <Badge key={idx} variant="outline" className="bg-green-500/10">
                        {med}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Concerns */}
              {checkIn.concerns && checkIn.concerns.length > 0 && (
                <div className="mb-4 rounded-lg bg-orange-500/10 p-4">
                  <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-orange-600">
                    <AlertCircle className="h-4 w-4" />
                    Concerns
                  </h4>
                  <ul className="space-y-1">
                    {checkIn.concerns.map((concern, idx) => (
                      <li key={idx} className="text-sm text-muted-foreground">
                        • {concern}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* AI Insights */}
              {checkIn.ai_insights && checkIn.ai_insights.length > 0 && (
                <div className="rounded-lg bg-primary-lighter p-4">
                  <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-primary">
                    <TrendingUp className="h-4 w-4" />
                    AI Insights & Recommendations
                  </h4>
                  <ul className="space-y-1">
                    {checkIn.ai_insights.map((insight, idx) => (
                      <li key={idx} className="text-sm text-foreground">
                        • {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}