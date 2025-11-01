import { useState, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload as UploadIcon, File, X, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
}

export default function Upload() {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      handleFiles(selectedFiles);
    }
  }, []);

  const handleFiles = (fileList: File[]) => {
    const newFiles: UploadedFile[] = fileList.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
    }));

    setFiles((prev) => [...prev, ...newFiles]);
    toast.success(`${fileList.length} file(s) uploaded successfully`);
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
    toast.info("File removed");
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-8 py-6">
        <h1 className="text-3xl font-bold text-foreground">Upload Reports</h1>
        <p className="mt-2 text-muted-foreground">
          Upload your lab reports, prescriptions, or medical documents
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Upload Area */}
          <Card
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={cn(
              "relative cursor-pointer border-2 border-dashed p-12 transition-smooth",
              isDragging
                ? "border-primary bg-primary-lighter"
                : "border-border hover:border-primary/50 hover:bg-muted/50"
            )}
          >
            <input
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={handleFileInput}
              className="absolute inset-0 cursor-pointer opacity-0"
            />
            <div className="flex flex-col items-center text-center">
              <div className="rounded-full bg-primary-lighter p-6">
                <UploadIcon className="h-10 w-10 text-primary" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-foreground">
                Drop files here or click to upload
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Supports PDF, JPG, PNG up to 10MB each
              </p>
              <Button className="mt-6" variant="default">
                Choose Files
              </Button>
            </div>
          </Card>

          {/* Uploaded Files List */}
          {files.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-foreground">
                  Uploaded Files ({files.length})
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setFiles([]);
                    toast.info("All files cleared");
                  }}
                >
                  Clear All
                </Button>
              </div>

              <div className="space-y-3">
                {files.map((file) => (
                  <Card
                    key={file.id}
                    className="p-4 transition-smooth hover:shadow-md"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="rounded-lg bg-primary-lighter p-2">
                          <File className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium text-foreground">
                            {file.name}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {formatFileSize(file.size)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-primary" />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(file.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              <Button className="w-full" size="lg">
                Process All Documents
              </Button>
            </div>
          )}

          {/* Info Card */}
          {files.length === 0 && (
            <Card className="p-6 bg-muted/50">
              <h3 className="mb-3 text-lg font-semibold text-foreground">
                What can you upload?
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Blood test results and lab reports</li>
                <li>• X-rays, MRIs, and scan images</li>
                <li>• Prescriptions and medication lists</li>
                <li>• Doctor's notes and consultation summaries</li>
              </ul>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
