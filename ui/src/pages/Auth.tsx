import React from "react";
import { motion } from "framer-motion";
import { StudentIcon, ChalkboardTeacherIcon, ShieldCheckIcon, ArrowRightIcon, GoogleLogoIcon } from "@phosphor-icons/react";
import { RoleCard } from "@/components/auth/RoleCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Logo } from "@/components/common/Logo";
import { useAuth } from "@/hooks/useAuth";
import { Spinner } from "@/components/common/Spinner";

const Auth: React.FC = () => {
  const { 
    role, 
    setRole, 
    email, 
    setEmail, 
    isLoading, 
    step, 
    setStep, 
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
              {step === 1 ? (
                <div className="space-y-6">
                    <h2 className="text-xl font-bold text-center text-foreground">Select your role</h2>
                    <div className="grid grid-cols-3 gap-3">
                      <RoleCard icon={StudentIcon} label="Student" selected={role === "student"} onClick={() => setRole("student")} />
                      <RoleCard icon={ChalkboardTeacherIcon} label="Faculty" selected={role === "faculty"} onClick={() => setRole("faculty")} />
                      <RoleCard icon={ShieldCheckIcon} label="Admin" selected={role === "admin"} onClick={() => setRole("admin")} />
                    </div>
                    <Button 
                      onClick={() => setStep(2)}
                      className="w-full h-14 text-lg font-bold rounded-xl flex items-center justify-center gap-2 group"
                    >
                      Continue <ArrowRightIcon weight="bold" className="group-hover:translate-x-1 transition-transform"/>
                    </Button>
                </div>
              ) : (
                <form onSubmit={handleLogin} className="space-y-6">
                  <div className="flex items-center gap-2 mb-6 cursor-pointer group" onClick={() => setStep(1)}>
                      <div className="p-1.5 rounded-full bg-secondary text-muted-foreground group-hover:text-foreground transition-colors">
                        <ArrowRightIcon className="rotate-180" size={16} />
                      </div>
                      <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">Change Role</span>
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

                  <Button 
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-14 text-lg font-bold rounded-xl shadow-lg shadow-primary/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {isLoading ? (
                        <Spinner />
                    ) : (
                        <>Login via SSO <ArrowRightIcon weight="bold"/></>
                    )}
                  </Button>

                  <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t border-border" />
                      </div>
                      <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
                      </div>
                    </div>

                    <Button variant="secondary" type="button" className="w-full h-12 rounded-xl flex items-center justify-center gap-2 font-medium">
                      <GoogleLogoIcon weight="bold" /> Google Workspace
                    </Button>
                </form>
              )}
            </motion.div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};


export default Auth;
