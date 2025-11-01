import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, FileText, TrendingUp, AlertCircle } from "lucide-react";

const checkInSummaries = [
  {
    id: 1,
    week: "Week of Jan 8 - Jan 14, 2025",
    date: "Jan 14, 2025",
    sentiment: "positive",
    keyPoints: [
      "Overall energy levels improved",
      "Sleep quality: 7-8 hours consistently",
      "Mild headache on Tuesday, resolved",
      "Active lifestyle maintained",
    ],
    concerns: [],
  },
  {
    id: 2,
    week: "Week of Jan 1 - Jan 7, 2025",
    date: "Jan 7, 2025",
    sentiment: "neutral",
    keyPoints: [
      "Energy dips in afternoons",
      "Sleep: 6-7 hours average",
      "Started new exercise routine",
    ],
    concerns: ["Occasional fatigue noted"],
  },
];

const reportSummaries = [
  {
    id: 1,
    title: "Blood Test Results",
    date: "Jan 10, 2025",
    type: "Lab Report",
    findings: [
      "Hemoglobin: Normal (14.5 g/dL)",
      "Blood Sugar: Slightly elevated (110 mg/dL)",
      "Cholesterol: Within range",
    ],
    recommendations: ["Monitor blood sugar levels", "Consider dietary adjustments"],
    status: "review",
  },
  {
    id: 2,
    title: "Prescription - Dr. Sharma",
    date: "Jan 5, 2025",
    type: "Prescription",
    findings: [
      "Vitamin D supplements prescribed",
      "Dosage: 2000 IU daily",
      "Duration: 3 months",
    ],
    recommendations: ["Take with meals for better absorption"],
    status: "active",
  },
];

export default function Summaries() {
  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-8 py-6">
        <h1 className="text-3xl font-bold text-foreground">Health Summaries</h1>
        <p className="mt-2 text-muted-foreground">
          Your weekly check-ins and medical report insights
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">
        <div className="mx-auto max-w-5xl space-y-8">
          {/* Check-In Summaries */}
          <section>
            <div className="mb-4 flex items-center gap-2">
              <Calendar className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold text-foreground">
                Weekly Check-In Summaries
              </h2>
            </div>
            <div className="space-y-4">
              {checkInSummaries.map((summary) => (
                <Card key={summary.id} className="p-6 transition-smooth hover:shadow-md">
                  <div className="mb-4 flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-foreground">
                        {summary.week}
                      </h3>
                      <p className="text-sm text-muted-foreground">{summary.date}</p>
                    </div>
                    <Badge
                      variant={
                        summary.sentiment === "positive"
                          ? "default"
                          : summary.sentiment === "neutral"
                          ? "secondary"
                          : "destructive"
                      }
                      className="capitalize"
                    >
                      {summary.sentiment}
                    </Badge>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                        <TrendingUp className="h-4 w-4 text-primary" />
                        Key Points
                      </h4>
                      <ul className="space-y-1">
                        {summary.keyPoints.map((point, idx) => (
                          <li key={idx} className="text-sm text-muted-foreground">
                            • {point}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {summary.concerns.length > 0 && (
                      <div className="rounded-lg bg-accent/10 p-3">
                        <h4 className="mb-1 flex items-center gap-2 text-sm font-medium text-accent">
                          <AlertCircle className="h-4 w-4" />
                          Concerns
                        </h4>
                        <ul className="space-y-1">
                          {summary.concerns.map((concern, idx) => (
                            <li key={idx} className="text-sm text-muted-foreground">
                              • {concern}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </section>

          {/* Report Summaries */}
          <section>
            <div className="mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold text-foreground">
                Medical Report Summaries
              </h2>
            </div>
            <div className="space-y-4">
              {reportSummaries.map((report) => (
                <Card key={report.id} className="p-6 transition-smooth hover:shadow-md">
                  <div className="mb-4 flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-foreground">
                        {report.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {report.type} • {report.date}
                      </p>
                    </div>
                    <Badge
                      variant={report.status === "active" ? "default" : "secondary"}
                    >
                      {report.status}
                    </Badge>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <h4 className="mb-2 text-sm font-medium text-foreground">
                        Findings
                      </h4>
                      <ul className="space-y-1">
                        {report.findings.map((finding, idx) => (
                          <li key={idx} className="text-sm text-muted-foreground">
                            • {finding}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="rounded-lg bg-primary-lighter p-3">
                      <h4 className="mb-1 text-sm font-medium text-primary">
                        Recommendations
                      </h4>
                      <ul className="space-y-1">
                        {report.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-sm text-foreground">
                            • {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
