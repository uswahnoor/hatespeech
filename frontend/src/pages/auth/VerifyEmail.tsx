import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Shield, CheckCircle, XCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function VerifyEmail() {
  const { token } = useParams<{ token: string }>();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setStatus("error");
        setMessage("Invalid verification token");
        return;
      }

      try {
        const data = await api.auth.verifyEmail(token);
        setStatus("success");
        setMessage(data.message || "Email verified successfully");
      } catch (error) {
        setStatus("error");
        setMessage(error instanceof Error ? error.message : "Email verification failed");
      }
    };

    verifyEmail();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Shield className="h-12 w-12 text-primary" />
          </div>
          <h1 className="text-3xl font-bold text-foreground">SafeSpeak</h1>
          <p className="text-muted-foreground">Email verification</p>
        </div>

        <Card className="shadow-soft">
          <CardHeader>
            <CardTitle className="flex items-center justify-center space-x-2">
              {status === "loading" && (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary" />
                  <span>Verifying...</span>
                </>
              )}
              {status === "success" && (
                <>
                  <CheckCircle className="h-5 w-5 text-success" />
                  <span>Verified!</span>
                </>
              )}
              {status === "error" && (
                <>
                  <XCircle className="h-5 w-5 text-destructive" />
                  <span>Error</span>
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground mb-6">{message}</p>
            
            {status !== "loading" && (
              <Button asChild className="bg-gradient-primary hover:opacity-90">
                <Link to="/auth/login">
                  Continue to Login
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}