import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";

export const useAuth = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>(""); // Added for backend integration
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSignUp, setIsSignUp] = useState<boolean>(false);
  const [step, setStep] = useState<number>(1);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (isSignUp) {
        await api.auth.register({ email, password });
        toast.success("Account created! Please sign in.");
        setIsSignUp(false);
      } else {
        const data = await api.auth.authenticate({ email, password });
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("userRole", data.role.toLowerCase());
        localStorage.setItem("userEmail", email);
        toast.success(`Logged in as ${data.role}`);
        navigate("/dashboard");
      }
    } catch (err) {
      const error = err as Error;
      toast.error(error.message || "Authentication failed");
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userEmail");
    navigate("/");
    toast.info("Logged out");
  };

  return {
    email,
    setEmail,
    password,
    setPassword,
    isLoading,
    isSignUp,
    setIsSignUp,
    step,
    setStep,
    handleLogin,
    logout,
    // Provide role from storage for UI parts that need it
    role: localStorage.getItem("userRole") || "student"
  };
};
