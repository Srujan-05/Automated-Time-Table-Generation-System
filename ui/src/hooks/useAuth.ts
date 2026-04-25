import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export const useAuth = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState<string>("student");
  const [email, setEmail] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [step, setStep] = useState<number>(1);

  const handleLogin = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      localStorage.setItem("userRole", role);
      toast.success(`Logged in as ${role}`);
      navigate("/dashboard");
    }, 1500);
  };

  const logout = () => {
    localStorage.removeItem("userRole");
    navigate("/");
    toast.info("Logged out");
  };

  return {
    role,
    setRole,
    email,
    setEmail,
    isLoading,
    step,
    setStep,
    handleLogin,
    logout
  };
};
