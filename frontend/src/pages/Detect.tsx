import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, AlertTriangle, CheckCircle, XCircle, Key } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface DetectionResult {
  classification: string;
  confidence: number;
  engine?: string;
  latency_ms?: number;
  sentiment?: string;
}

interface ApiKey {
  id: number;
  key: string;
  created_at: string;
}

export default function Detect() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [selectedApiKey, setSelectedApiKey] = useState<string>("");
  const { toast } = useToast();

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const keys = await api.user.getApiKeys();
      setApiKeys(keys);
      if (keys.length > 0) {
        setSelectedApiKey(keys[0].key);
      }
    } catch (error) {
      console.error("Failed to fetch API keys:", error);
    }
  };

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast({
        title: "No text provided",
        description: "Please enter some text to analyze",
        variant: "destructive",
      });
      return;
    }

    if (!selectedApiKey) {
      console.log('No API key selected, proceeding without API key for testing');
      // Allow testing without API key
    }

    setIsLoading(true);

    try {
      console.log('Sending request with API key:', selectedApiKey);
      const data = await api.detect.analyzeText(text, selectedApiKey);
      console.log('Received response:', data);
      setResult({
        classification: data.classification,
        confidence: data.confidence,
        engine: data.engine,
        latency_ms: data.latency_ms,
        sentiment: data.sentiment,
      });
      
      toast({
        title: "Analysis complete",
        description: "Text has been analyzed successfully",
      });
    } catch (error) {
      toast({
        title: "Analysis failed",
        description: error instanceof Error ? error.message : "Failed to analyze text",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getClassificationColor = (classification: string) => {
    switch (classification.toLowerCase()) {
      case "hate":
      case "toxic":
      case "harmful":
        return "destructive";
      case "safe":
      case "clean":
        return "success";
      default:
        return "secondary";
    }
  };

  const getClassificationIcon = (classification: string) => {
    switch (classification.toLowerCase()) {
      case "hate":
      case "toxic":
      case "harmful":
        return XCircle;
      case "safe":
      case "clean":
        return CheckCircle;
      default:
        return AlertTriangle;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-foreground mb-4">
          Text Analysis
        </h1>
        <p className="text-xl text-muted-foreground">
          Analyze text content for hate speech and harmful language
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-5 w-5" />
              <span>Text Input</span>
            </CardTitle>
            <CardDescription>
              Enter the text you want to analyze for harmful content
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* API Key Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">API Key</label>
              {apiKeys.length > 0 ? (
                <Select value={selectedApiKey} onValueChange={setSelectedApiKey}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select an API key" />
                  </SelectTrigger>
                  <SelectContent>
                    {apiKeys.map((key) => (
                      <SelectItem key={key.id} value={key.key}>
                        <div className="flex items-center gap-2">
                          <Key className="h-4 w-4" />
                          <span className="font-mono text-xs">
                            {key.key.substring(0, 8)}...{key.key.substring(key.key.length - 8)}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Alert>
                  <Key className="h-4 w-4" />
                  <AlertDescription>
                    No API keys found. <a href="/api-keys" className="text-primary hover:underline">Create an API key</a> to use the detection service.
                  </AlertDescription>
                </Alert>
              )}
            </div>

            <Textarea
              placeholder="Enter text to analyze..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={8}
              className="resize-none"
            />
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {text.length} characters
              </span>
              <Button
                onClick={handleAnalyze}
                disabled={isLoading || !text.trim() || !selectedApiKey}
                className="bg-gradient-primary hover:opacity-90"
              >
                {isLoading ? "Analyzing..." : "Analyze Text"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
            <CardDescription>
              AI-powered content classification and confidence score
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!result ? (
              <div className="text-center py-12">
                <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Enter text and click "Analyze Text" to see results
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="text-center">
                  <div className="mb-4">
                    {(() => {
                      const Icon = getClassificationIcon(result.classification);
                      return <Icon className="h-16 w-16 mx-auto text-muted-foreground" />;
                    })()}
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold">Classification</h3>
                    <Badge 
                      variant={getClassificationColor(result.classification) as any}
                      className="text-lg px-4 py-2"
                    >
                      {result.classification}
                    </Badge>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Confidence Score</h4>
                  <div className="bg-muted rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all duration-500"
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {(result.confidence * 100).toFixed(1)}% confidence
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-1">Engine</h4>
                    <p className="text-sm text-muted-foreground">{result.engine || "n/a"}</p>
                  </div>
                  <div>
                    <h4 className="font-medium mb-1">Latency</h4>
                    <p className="text-sm text-muted-foreground">{result.latency_ms ? `${result.latency_ms} ms` : "n/a"}</p>
                  </div>
                  {result.sentiment && (
                    <div className="col-span-2">
                      <h4 className="font-medium mb-1">Sentiment</h4>
                      <p className="text-sm text-muted-foreground">{result.sentiment}</p>
                    </div>
                  )}
                </div>

                {result.classification.toLowerCase() !== "safe" && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      This content may contain harmful or inappropriate language. 
                      Please review and moderate accordingly.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Usage Guidelines */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle>Usage Guidelines</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>• Analysis results are AI-generated and should be used as guidance</li>
            <li>• Always apply human judgment for final moderation decisions</li>
            <li>• The system is designed to err on the side of caution</li>
            <li>• Context and intent may require manual review</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}