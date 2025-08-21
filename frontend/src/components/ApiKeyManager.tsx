import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trash2, Key, Plus, ExternalLink, Copy } from 'lucide-react';

interface ApiKey {
  id: number;
  key: string;
  created_at: string;
}

const ApiKeyManager: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const { toast } = useToast();

  const fetchApiKeys = async () => {
    setLoading(true);
    try {
      const data = await api.user.getApiKeys();
      setApiKeys(data);
    } catch (error) {
      toast({
        title: "Failed to fetch API keys",
        description: error instanceof Error ? error.message : "Could not load API keys",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async () => {
    setCreating(true);
    try {
      const newKey = await api.user.createApiKey();
      setApiKeys([...apiKeys, newKey]);
      toast({
        title: "API key created",
        description: "Your new API key has been generated successfully.",
      });
    } catch (error) {
      toast({
        title: "Failed to create API key",
        description: error instanceof Error ? error.message : "Could not create API key",
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  };

  const deleteApiKey = async (id: number) => {
    try {
      await api.user.deleteApiKey(id);
      setApiKeys(apiKeys.filter(k => k.id !== id));
      toast({
        title: "API key deleted",
        description: "The API key has been removed successfully.",
      });
    } catch (error) {
      toast({
        title: "Failed to delete API key",
        description: error instanceof Error ? error.message : "Could not delete API key",
        variant: "destructive",
      });
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "API key copied successfully",
    });
  };

  useEffect(() => {
    fetchApiKeys();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">API Keys</h2>
          <p className="text-muted-foreground">Manage your API keys for hate speech detection</p>
        </div>
        <Button
          onClick={createApiKey}
          disabled={apiKeys.length >= 2 || creating}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          {creating ? 'Creating...' : 'Create API Key'}
        </Button>
      </div>

      {loading ? (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-center">
              <div className="text-muted-foreground">Loading API keys...</div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {apiKeys.length === 0 ? (
            <Card>
              <CardContent className="p-6">
                <div className="text-center text-muted-foreground">
                  <Key className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No API keys found. Create your first API key to get started.</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            apiKeys.map(key => (
              <Card key={key.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-sm font-mono bg-muted p-2 rounded flex-1">
                          {key.key}
                        </CardTitle>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(key.key)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                      <CardDescription>
                        Created: {new Date(key.created_at).toLocaleDateString()}
                      </CardDescription>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteApiKey(key.id)}
                      className="text-destructive hover:text-destructive ml-2"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
              </Card>
            ))
          )}
        </div>
      )}

      {apiKeys.length >= 2 && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">Limit Reached</Badge>
              <span className="text-sm text-muted-foreground">
                You can only have 2 API keys. Delete an existing key to create a new one.
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* External API Usage Documentation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ExternalLink className="h-5 w-5" />
            Use in Your Applications
          </CardTitle>
          <CardDescription>
            Integrate our hate speech detection API into your applications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2">API Endpoint</h4>
            <code className="bg-muted p-2 rounded block text-sm">
              POST http://localhost:8000/api/detect/
            </code>
          </div>
          
          <div>
            <h4 className="font-semibold mb-2">Example Request</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`curl -X POST http://localhost:8000/api/detect/ \\
  -H "Content-Type: application/json" \\
  -H "X-API-KEY: your-api-key-here" \\
  -d '{"text": "Hello, how are you today?"}'`}
            </pre>
          </div>

          <div>
            <h4 className="font-semibold mb-2">Response</h4>
            <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`{
  "classification": "safe",
  "confidence": 0.95,
  "sentiment": "positive",
  "engine": "transformer",
  "latency_ms": 145.2
}`}
            </pre>
          </div>

          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.open('http://localhost:8000/api/docs/', '_blank')}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              JSON Documentation
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => window.open('http://localhost:8000/api/docs/html/', '_blank')}
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Full Documentation
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ApiKeyManager;
