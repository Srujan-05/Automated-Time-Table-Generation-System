import React from "react";
import { motion } from "framer-motion";
import { SignInIcon, UserPlusIcon } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Logo } from "@/components/common/Logo";
import { useAuth } from "@/hooks/useAuth";
import { Spinner } from "@/components/common/Spinner";

const Auth: React.FC = () => {
  const { 
    email, 
    setEmail, 
    password,
    setPassword,
    isLoading,
    isSignUp,
    setIsSignUp,
    handleLogin 
  } = useAuth();

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-4 relative overflow-hidden font-sans">
      
      {/* Background Effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[120px]" />
      
      <div className="w-full max-w-md relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10 flex flex-col items-center"
        >
          <Logo className="scale-150 mb-8" />
          <p className="text-muted-foreground text-lg">Academic Scheduling, Perfected.</p>
        </motion.div>

        <Card className="bg-card/50 backdrop-blur-xl border-border/50 rounded-3xl shadow-2xl overflow-hidden">
          <CardContent className="p-8">
            <motion.div layout>
                <form onSubmit={handleLogin} className="space-y-6">
                  <div className="text-center mb-4">
                    <h2 className="text-xl font-bold text-foreground">
                        {isSignUp ? "Create Account" : "Welcome Back"}
                    </h2>
                    <p className="text-sm text-muted-foreground mt-1">
                        Use your university credentials to continue.
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-muted-foreground">Institutional Email</Label>
                    <Input 
                        id="email"
                        type="email" 
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="id@college.edu"
                        className="h-12 rounded-xl bg-background/50 font-mono"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-muted-foreground">Password</Label>
                    <Input 
                        id="password"
                        type="password" 
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="h-12 rounded-xl bg-background/50"
                    />
                  </div>

                  <Button 
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-14 text-lg font-bold rounded-xl shadow-lg shadow-primary/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {isLoading ? (
                        <Spinner />
                    ) : isSignUp ? (
                        <>Create Account <UserPlusIcon weight="bold"/></>
                    ) : (
                        <>Sign In <SignInIcon weight="bold"/></>
                    )}
                  </Button>

                  <div className="relative py-2">
                      <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t border-border" />
                      </div>
                    </div>

                    <Button 
                      variant="ghost" 
                      type="button" 
                      onClick={() => setIsSignUp(!isSignUp)}
                      className="w-full h-12 rounded-xl flex items-center justify-center gap-2 font-medium hover:bg-primary/5"
                    >
                      {isSignUp ? (
                          <>Already have an account? <span className="text-primary font-bold">Sign In</span></>
                      ) : (
                          <>Need an account? <span className="text-primary font-bold">Sign Up</span></>
                      )}
                    </Button>
                </form>
            </motion.div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};


export default Auth;
