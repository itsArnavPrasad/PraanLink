import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar, TrendingUp, AlertCircle, Heart, Moon, Zap, Pill, ActivitySquare, FileText, Stethoscope, FlaskConical, FileDown, Loader2, ExternalLink } from "lucide-react";
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

interface PrescriptionSummary {
  id: number;
  timestamp: string;
  prescription_date: string;
  doctor_name: string;
  doctor_qualification: string;
  hospital: string;
  patient_name: string;
  patient_age: string;
  patient_gender: string;
  medicines: Array<{
    name: string;
    dosage: string;
    frequency: string;
    duration: string;
    special_instructions: string;
  }>;
  diagnosis: string;
  symptoms: string;
  advice: string;
  follow_up: string;
  prescription_summary: string;
}

interface ReportSummary {
  id: number;
  timestamp: string;
  report_date: string;
  report_time: string;
  metrics: Array<{
    test_name: string;
    category: string;
    value: string;
    unit: string;
    reference_range: string;
    interpretation: string;
  }>;
  analyzed_metrics: Array<{
    test_name: string;
    status: string;
    value: string;
    unit: string;
    reference_range: string;
    interpretation: string;
  }>;
  overall_health_risk_index: number;
  severity: string;
  critical_flags: string[];
  lab_summary_overview: string;
  key_findings: Array<{
    metric: string;
    value: string;
    interpretation: string;
  }>;
  overall_risk: string;
  recommendations: string[];
  critical_alerts: string[];
}

export default function Summaries() {
  const [checkIns, setCheckIns] = useState<CheckInSummary[]>([]);
  const [prescriptions, setPrescriptions] = useState<PrescriptionSummary[]>([]);
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("checkins");
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [pdfPath, setPdfPath] = useState<string | null>(null);
  const [reportId, setReportId] = useState<number | null>(null);

  const BACKEND_URL = 'http://localhost:8000';

  const fetchLatestOverallReport = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/latest-overall-report`);
      
      if (response.ok) {
        const result = await response.json();
        if (result.pdf_file_path) {
          setReportId(result.id);
          // Convert backend file path to URL
          const pdfUrl = `${BACKEND_URL}/${result.pdf_file_path}`;
          setPdfPath(pdfUrl);
        }
      } else if (response.status !== 404) {
        // Only log non-404 errors (404 means no report exists yet, which is fine)
        const errorData = await response.json();
        console.error("Error fetching latest overall report:", errorData);
      }
    } catch (error) {
      console.error("Error fetching latest overall report:", error);
    }
  };

  const fetchAllData = async () => {
    try {
      const [checkInsRes, prescriptionsRes, reportsRes] = await Promise.all([
        fetch(`${BACKEND_URL}/checkins/summaries?limit=20`),
        fetch(`${BACKEND_URL}/api/prescriptions/summaries?limit=20`),
        fetch(`${BACKEND_URL}/api/reports/summaries?limit=20`)
      ]);

      const [checkInsData, prescriptionsData, reportsData] = await Promise.all([
        checkInsRes.json(),
        prescriptionsRes.json(),
        reportsRes.json()
      ]);

      if (checkInsData.success) setCheckIns(checkInsData.checkins);
      if (prescriptionsData.success) setPrescriptions(prescriptionsData.prescriptions);
      if (reportsData.success) setReports(reportsData.reports);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    fetchLatestOverallReport();
  }, []);

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

  const getScoreColor = (score: string | number) => {
    const scoreNum = typeof score === 'string' ? parseInt(score) : score;
    if (scoreNum >= 80) return 'text-green-500';
    if (scoreNum >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getSeverityColor = (severity: string) => {
    const sev = severity?.toLowerCase() || '';
    if (sev.includes('low') || sev.includes('normal')) return 'default';
    if (sev.includes('moderate') || sev.includes('medium')) return 'secondary';
    return 'destructive';
  };

  const handleGenerateOverallReport = async () => {
    setIsGeneratingReport(true);
    setPdfPath(null);
    setReportId(null);

    try {
      const response = await fetch(`${BACKEND_URL}/generate-overall-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to generate report');
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        setReportId(result.id);
        // Convert backend file path to URL
        // The backend stores paths like "uploads/overall_reports/OverallReport_xxx.pdf"
        // We need to convert it to a URL the frontend can access
        const pdfUrl = `${BACKEND_URL}/${result.pdf_file_path}`;
        setPdfPath(pdfUrl);
        toast.success('Overall report generated successfully!');
        // Refresh the latest report in case we want to show updated info
        await fetchLatestOverallReport();
      } else {
        throw new Error(result.message || 'Report generation failed');
      }
    } catch (error: any) {
      console.error('Error generating overall report:', error);
      toast.error(error.message || 'Failed to generate overall report');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full flex-col">
        <div className="border-b border-border bg-card px-8 py-6">
          <h1 className="text-3xl font-bold text-foreground">Health Summaries</h1>
          <p className="mt-2 text-muted-foreground">
            Your complete health history and insights
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

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border bg-card px-8 py-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Health Summaries</h1>
            <p className="mt-2 text-muted-foreground">
              Your complete health history and insights
            </p>
          </div>
          <div className="flex flex-col items-end gap-3">
            <Button
              onClick={handleGenerateOverallReport}
              disabled={isGeneratingReport}
              className="flex items-center gap-2"
            >
              {isGeneratingReport ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generating Report...
                </>
              ) : (
                <>
                  <FileDown className="h-4 w-4" />
                  Prepare Overall Report
                </>
              )}
            </Button>
            {pdfPath && (
              <a
                href={pdfPath}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-primary hover:underline"
              >
                <ExternalLink className="h-4 w-4" />
                View Generated PDF Report
              </a>
            )}
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className="border-b border-border bg-card px-8">
          <TabsList className="bg-transparent">
            <TabsTrigger value="checkins" className="flex items-center gap-2">
              <Heart className="h-4 w-4" />
              Check-ins ({checkIns.length})
            </TabsTrigger>
            <TabsTrigger value="prescriptions" className="flex items-center gap-2">
              <Stethoscope className="h-4 w-4" />
              Prescriptions ({prescriptions.length})
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <FlaskConical className="h-4 w-4" />
              Lab Reports ({reports.length})
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-auto">
          <TabsContent value="checkins" className="p-8 mt-0">
            {checkIns.length === 0 ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <Heart className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No Check-Ins Yet</h3>
                  <p className="text-muted-foreground">Start your first daily check-in to see summaries here</p>
                </div>
              </div>
            ) : (
              <div className="mx-auto max-w-5xl space-y-6">
                {checkIns.map((checkIn) => (
                  <Card key={checkIn.id} className="p-6 transition-all hover:shadow-md">
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

                    {checkIn.summary && (
                      <div className="mb-4 rounded-lg bg-muted/50 p-4">
                        <p className="text-sm text-foreground leading-relaxed">{checkIn.summary}</p>
                      </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      {checkIn.sleep_quality && (
                        <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-500/10">
                          <Moon className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="text-sm font-medium text-foreground">Sleep Quality</p>
                            <p className="text-sm text-muted-foreground">{checkIn.sleep_quality}</p>
                          </div>
                        </div>
                      )}
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

                    {checkIn.symptoms && checkIn.symptoms.length > 0 && (
                      <div className="mb-4">
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                          <ActivitySquare className="h-4 w-4 text-red-500" />
                          Symptoms Reported
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {checkIn.symptoms.map((symptom, idx) => (
                            <Badge key={idx} variant="outline" className="bg-red-500/10">{symptom}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {checkIn.medications_taken && checkIn.medications_taken.length > 0 && (
                      <div className="mb-4">
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                          <Pill className="h-4 w-4 text-green-500" />
                          Medications Taken
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {checkIn.medications_taken.map((med, idx) => (
                            <Badge key={idx} variant="outline" className="bg-green-500/10">{med}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {checkIn.ai_insights && checkIn.ai_insights.length > 0 && (
                      <div className="rounded-lg bg-primary/10 p-4">
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-primary">
                          <TrendingUp className="h-4 w-4" />
                          AI Insights & Recommendations
                        </h4>
                        <ul className="space-y-1">
                          {checkIn.ai_insights.map((insight, idx) => (
                            <li key={idx} className="text-sm text-foreground">• {insight}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="prescriptions" className="p-8 mt-0">
            {prescriptions.length === 0 ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <Stethoscope className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No Prescriptions Yet</h3>
                  <p className="text-muted-foreground">Upload your first prescription to see summaries here</p>
                </div>
              </div>
            ) : (
              <div className="mx-auto max-w-5xl space-y-6">
                {prescriptions.map((prescription) => (
                  <Card key={prescription.id} className="p-6 transition-all hover:shadow-md">
                    <div className="mb-4 flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-primary" />
                          <h3 className="text-lg font-semibold text-foreground">
                            {prescription.prescription_date || formatDate(prescription.timestamp)}
                          </h3>
                        </div>
                        {prescription.doctor_name && (
                          <p className="mt-1 text-sm text-muted-foreground">
                            Dr. {prescription.doctor_name} {prescription.doctor_qualification && `(${prescription.doctor_qualification})`}
                          </p>
                        )}
                        {prescription.hospital && (
                          <p className="text-sm text-muted-foreground">{prescription.hospital}</p>
                        )}
                      </div>
                      {prescription.patient_name && (
                        <div className="text-right">
                          <Badge variant="outline">{prescription.patient_name}</Badge>
                          {(prescription.patient_age || prescription.patient_gender) && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {prescription.patient_age && `${prescription.patient_age}yr`}
                              {prescription.patient_age && prescription.patient_gender && ' • '}
                              {prescription.patient_gender}
                            </p>
                          )}
                        </div>
                      )}
                    </div>

                    {prescription.prescription_summary && (
                      <div className="mb-4 rounded-lg bg-muted/50 p-4">
                        <p className="text-sm text-foreground leading-relaxed">{prescription.prescription_summary}</p>
                      </div>
                    )}

                    {prescription.symptoms && (
                      <div className="mb-4">
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-foreground">
                          <ActivitySquare className="h-4 w-4 text-orange-500" />
                          Symptoms
                        </h4>
                        <p className="text-sm text-muted-foreground">{prescription.symptoms}</p>
                      </div>
                    )}

                    {prescription.diagnosis && (
                      <div className="mb-4 rounded-lg bg-blue-500/10 p-4">
                        <h4 className="mb-2 text-sm font-medium text-blue-600">Diagnosis</h4>
                        <p className="text-sm text-foreground">{prescription.diagnosis}</p>
                      </div>
                    )}

                    {prescription.medicines && prescription.medicines.length > 0 && (
                      <div className="mb-4">
                        <h4 className="mb-3 flex items-center gap-2 text-sm font-medium text-foreground">
                          <Pill className="h-4 w-4 text-green-500" />
                          Prescribed Medications
                        </h4>
                        <div className="space-y-2">
                          {prescription.medicines.map((med, idx) => (
                            <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-green-500/10">
                              <div className="flex-1">
                                <p className="font-medium text-sm text-foreground">{med.name}</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                  {med.dosage && `${med.dosage}`}
                                  {med.frequency && ` • ${med.frequency}`}
                                  {med.duration && ` • ${med.duration}`}
                                </p>
                                {med.special_instructions && (
                                  <p className="text-xs text-muted-foreground mt-1 italic">{med.special_instructions}</p>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {prescription.advice && (
                      <div className="mb-4 rounded-lg bg-purple-500/10 p-4">
                        <h4 className="mb-2 text-sm font-medium text-purple-600">Advice</h4>
                        <p className="text-sm text-foreground">{prescription.advice}</p>
                      </div>
                    )}

                    {prescription.follow_up && (
                      <div className="rounded-lg bg-yellow-500/10 p-4">
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-yellow-600">
                          <Calendar className="h-4 w-4" />
                          Follow-up
                        </h4>
                        <p className="text-sm text-foreground">{prescription.follow_up}</p>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="reports" className="p-8 mt-0">
            {reports.length === 0 ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <FlaskConical className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No Lab Reports Yet</h3>
                  <p className="text-muted-foreground">Upload your first lab report to see summaries here</p>
                </div>
              </div>
            ) : (
              <div className="mx-auto max-w-5xl space-y-6">
                {reports.map((report) => (
                  <Card key={report.id} className="p-6 transition-all hover:shadow-md">
                    <div className="mb-4 flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <FlaskConical className="h-5 w-5 text-primary" />
                          <h3 className="text-lg font-semibold text-foreground">
                            {report.report_date || formatDate(report.timestamp)}
                            {report.report_time && ` at ${report.report_time}`}
                          </h3>
                        </div>
                        {report.overall_health_risk_index !== null && (
                          <p className={`mt-1 text-sm font-medium ${getScoreColor(100 - report.overall_health_risk_index)}`}>
                            Health Risk Index: {report.overall_health_risk_index}
                          </p>
                        )}
                      </div>
                      {report.severity && (
                        <Badge variant={getSeverityColor(report.severity)} className="capitalize">
                          {report.severity}
                        </Badge>
                      )}
                    </div>

                    {report.lab_summary_overview && (
                      <div className="mb-4 rounded-lg bg-muted/50 p-4">
                        <p className="text-sm text-foreground leading-relaxed">{report.lab_summary_overview}</p>
                      </div>
                    )}

                    {report.critical_alerts && report.critical_alerts.length > 0 && (
                      <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 p-4">
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-red-600">
                          <AlertCircle className="h-4 w-4" />
                          Critical Alerts
                        </h4>
                        <ul className="space-y-1">
                          {report.critical_alerts.map((alert, idx) => (
                            <li key={idx} className="text-sm text-red-600">• {alert}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {report.analyzed_metrics && report.analyzed_metrics.length > 0 && (
                      <div className="mb-4">
                        <h4 className="mb-3 text-sm font-medium text-foreground">Test Results</h4>
                        <div className="space-y-2">
                          {report.analyzed_metrics.slice(0, 100).map((metric, idx) => (
                            <div key={idx} className="flex items-center justify-between p-2 rounded bg-blue-500/10">
                              <div className="flex-1">
                                <p className="text-sm font-medium text-foreground">{metric.test_name}</p>
                                <p className="text-xs text-muted-foreground">{metric.reference_range}</p>
                              </div>
                              <div className="text-right">
                                <p className="text-sm font-medium">{metric.value} {metric.unit}</p>
                                <Badge variant={metric.status?.toLowerCase().includes('abnormal') ? 'destructive' : 'outline'} className="text-xs">
                                  {metric.status || 'Normal'}
                                </Badge>
                              </div>
                            </div>
                          ))}
                          {report.analyzed_metrics.length > 100 && (
                            <p className="text-xs text-center text-muted-foreground pt-2">
                              +{report.analyzed_metrics.length - 100} more tests
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    {report.recommendations && report.recommendations.length > 0 && (
                      <div className="rounded-lg bg-primary/10 p-4">
                        <h4 className="mb-2 flex items-center gap-2 text-sm font-medium text-primary">
                          <TrendingUp className="h-4 w-4" />
                          Recommendations
                        </h4>
                        <ul className="space-y-1">
                          {report.recommendations.map((rec, idx) => (
                            <li key={idx} className="text-sm text-foreground">• {rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}