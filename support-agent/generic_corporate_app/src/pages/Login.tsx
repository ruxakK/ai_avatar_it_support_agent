import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

const Login = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const checkBlockedUser = async (username: string): Promise<boolean> => {
    try {
      const response = await fetch("/blockusers.txt");
      const text = await response.text();
      const blockedUsers = text.split("\n").map(u => u.trim().toLowerCase());
      
      // Extract just the username part after the last backslash
      const usernamePart = username.split("\\").pop()?.toLowerCase() || "";
      
      return blockedUsers.includes(usernamePart);
    } catch (error) {
      console.error("Error checking blocked users:", error);
      return false;
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Check if user is blocked
    const isBlocked = await checkBlockedUser(username);
    
    if (isBlocked) {
      setError("Your account has been blocked. Please reach out to support for help.");
      setLoading(false);
      return;
    }

    // Hard-coded credentials check
    if (username === "\\vienna\\maxman123" && password === "passw0rd") {
      // Store auth state
      localStorage.setItem("isAuthenticated", "true");
      localStorage.setItem("username", username);
      navigate("/dashboard");
    } else {
      setError("Invalid username or password. Please try again.");
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-secondary/30 p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-2 text-center">
          <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-2">
            <span className="text-xl font-bold text-primary-foreground">GCA</span>
          </div>
          <CardTitle className="text-2xl font-bold">GenericCorporateApp</CardTitle>
          <CardDescription>Sign in to your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="\domain\username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="transition-all"
              />
              <p className="text-sm text-muted-foreground">
                Type in your username like this: <span className="font-mono">\domain\username</span>
              </p>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="transition-all"
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit" 
              className="w-full" 
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;
