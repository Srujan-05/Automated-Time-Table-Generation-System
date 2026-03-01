
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Student, ChalkboardTeacher, ShieldCheck, ArrowRight, GoogleLogo } from "@phosphor-icons/react";
import type { RoleCardProps } from "../lib/types";

const RoleCard: React.FC<RoleCardProps> = ({ icon: Icon, label, selected, onClick }) => (
  <motion.button
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className={`
      flex flex-col items-center justify-center p-6 rounded-2xl border-2 transition-all duration-300 w-full
      ${selected 
        ? "border-red-500 bg-red-500/10 shadow-[0_0_30px_rgba(239,68,68,0.2)]" 
        : "border-zinc-800 bg-zinc-900/50 hover:border-zinc-700 hover:bg-zinc-800"
      }
    `}
  >
    <div className={`p-4 rounded-full mb-4 ${selected ? "bg-red-500 text-white" : "bg-zinc-800 text-zinc-400"}`}>
      <Icon weight={selected ? "fill" : "regular"} className="w-8 h-8" />
    </div>
    <span className={`font-sans font-medium text-lg ${selected ? "text-white" : "text-zinc-400"}`}>
      {label}
    </span>
  </motion.button>
);

const Auth: React.FC = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState<string>("student");
  const [email, setEmail] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [step, setStep] = useState<number>(1); // 1: Role, 2: Login

  const handleLogin = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      navigate("/dashboard");
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 relative overflow-hidden">
      
      {/* Background Effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-red-600/20 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-red-900/10 rounded-full blur-[120px]" />
      
      <div className="w-full max-w-md relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-red-500 to-red-700 shadow-[0_0_40px_rgba(239,68,68,0.5)] mb-6 rotate-3 hover:rotate-6 transition-transform">
             <span className="text-3xl font-bold text-white">T</span>
          </div>
          <h1 className="text-4xl font-sans font-bold text-white tracking-tight mb-2">Time<span className="text-red-500">Sync</span></h1>
          <p className="text-zinc-400 text-lg">Academic Scheduling, Perfected.</p>
        </motion.div>

        <motion.div 
            layout
            className="bg-zinc-950/50 backdrop-blur-xl border border-zinc-800/50 p-8 rounded-3xl shadow-2xl"
        >
          {step === 1 ? (
             <div className="space-y-6">
                <h2 className="text-xl font-medium text-center text-zinc-200">Select your role</h2>
                <div className="grid grid-cols-3 gap-3">
                  <RoleCard icon={Student} label="Student" selected={role === "student"} onClick={() => setRole("student")} />
                  <RoleCard icon={ChalkboardTeacher} label="Faculty" selected={role === "faculty"} onClick={() => setRole("faculty")} />
                  <RoleCard icon={ShieldCheck} label="Admin" selected={role === "admin"} onClick={() => setRole("admin")} />
                </div>
                <button 
                  onClick={() => setStep(2)}
                  className="w-full py-4 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-colors flex items-center justify-center gap-2 group"
                >
                  Continue <ArrowRight weight="bold" className="group-hover:translate-x-1 transition-transform"/>
                </button>
             </div>
          ) : (
            <form onSubmit={handleLogin} className="space-y-6">
               <div className="flex items-center gap-2 mb-6 cursor-pointer" onClick={() => setStep(1)}>
                  <div className="p-1 rounded-full bg-zinc-800/50 text-zinc-400 hover:text-white">
                    <ArrowRight className="rotate-180" />
                  </div>
                  <span className="text-sm text-zinc-500 hover:text-zinc-300">Change Role</span>
               </div>
               
               <div>
                 <label className="block text-sm font-medium text-zinc-400 mb-2">Institutional Email</label>
                 <input 
                    type="email" 
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="id@college.edu"
                    className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-all font-mono"
                 />
               </div>

               <button 
                 type="submit"
                 disabled={isLoading}
                 className="w-full py-4 bg-gradient-to-r from-red-600 to-red-500 text-white font-bold rounded-xl hover:shadow-[0_0_20px_rgba(239,68,68,0.4)] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
               >
                 {isLoading ? (
                    <span className="animate-pulse">Verifying...</span>
                 ) : (
                    <>Login via SSO <ArrowRight weight="bold"/></>
                 )}
               </button>

               <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-zinc-800" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-[#050505] px-2 text-zinc-500">Or continue with</span>
                  </div>
                </div>

                <button type="button" className="w-full py-3 bg-zinc-900 border border-zinc-800 text-zinc-300 font-medium rounded-xl hover:bg-zinc-800 transition-colors flex items-center justify-center gap-2">
                  <GoogleLogo weight="bold" className="text-white"/> Google Workspace
                </button>
            </form>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Auth;
