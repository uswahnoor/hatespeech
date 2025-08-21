import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { History as HistoryIcon, RefreshCw, Search } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Link } from "react-router-dom";

interface HistoryItem {
  id: string;
  text: string;
  classification: string;
  confidence: number;
  created_at: string;
}

export default function History() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  const fetchHistory = async () => {
    try {
      const data = await api.detect.getHistory();
      setHistory(data);
    } catch (error) {
      toast({
        title: "Failed to load history",
        description: error instanceof Error ? error.message : "Could not load analysis history",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

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

  const truncateText = (text: string, maxLength: number = 100) => {
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading analysis history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-4">
            Analysis History
          </h1>
          <p className="text-xl text-muted-foreground">
            Review your previous text analyses and results
          </p>
        </div>
        <Button
          onClick={fetchHistory}
          variant="outline"
          size="sm"
          className="flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </Button>
      </div>

      {history.length === 0 ? (
        <Card className="shadow-soft">
          <CardContent className="text-center py-12">
            <HistoryIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Analysis History</h3>
            <p className="text-muted-foreground mb-6">
              You haven't analyzed any text yet. Start by analyzing some content.
            </p>
            <Button asChild className="bg-gradient-primary hover:opacity-90">
              <Link to="/detect">
                <Search className="h-4 w-4 mr-2" />
                Analyze Text
              </Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground">
            Showing {history.length} analysis result{history.length !== 1 ? 's' : ''}
          </div>
          
          <div className="grid gap-4">
            {history.map((item) => (
              <Card key={item.id} className="shadow-soft hover:shadow-glow transition-all duration-300">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <Badge 
                        variant={getClassificationColor(item.classification) as any}
                        className="text-xs"
                      >
                        {item.classification}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {(item.confidence * 100).toFixed(1)}% confidence
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-foreground leading-relaxed">
                    {truncateText(item.text)}
                  </p>
                  {item.text.length > 100 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="mt-2 p-0 h-auto text-primary hover:text-primary/80"
                    >
                      Show more
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}