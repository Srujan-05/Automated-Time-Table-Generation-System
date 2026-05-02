import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export const usePreferences = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedShift, setSelectedShift] = useState<number>(1);
  const [professors, setProfessors] = useState<{id: number, name: string, email: string}[]>([]);
  const [selectedProfessorId, setSelectedProfessorId] = useState<string>("");

  const role = localStorage.getItem("userRole")?.toLowerCase();
  const isAdmin = role === 'admin';
  const isFaculty = role === 'faculty';

  const fetchProfessorShift = useCallback(async (id: number) => {
    try {
        const res = await api.preferences.fetchShift(id);
        setSelectedShift(res.bin_id);
    } catch (err) {
        toast.error("Failed to fetch professor preference");
        console.error(err);
    }
  }, []);

  const fetchInitialData = useCallback(async () => {
    setIsLoading(true);
    try {
      if (isAdmin) {
        const profList = await api.preferences.listFaculty();
        setProfessors(profList);
        
        // Auto-select first professor if list not empty
        if (profList.length > 0) {
            const firstProfId = profList[0].id.toString();
            setSelectedProfessorId(firstProfId);
            const res = await api.preferences.fetchShift(Number(firstProfId));
            setSelectedShift(res.bin_id);
        }
      } else {
        // Faculty loading their own
        const res = await api.preferences.fetchShift();
        setSelectedShift(res.bin_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  const handleProfessorChange = (val: string) => {
    setSelectedProfessorId(val);
    fetchProfessorShift(Number(val));
  };

  const submitPreferences = async () => {
    setIsSubmitting(true);
    try {
      const targetId = isAdmin ? Number(selectedProfessorId) : undefined;
      await api.preferences.updateShift(selectedShift, targetId);
      toast.success(`Preferences updated successfully`);
    } catch (err) {
      toast.error("Failed to update preferences");
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    isLoading,
    isSubmitting,
    selectedShift,
    setSelectedShift,
    submitPreferences,
    isAdmin,
    isFaculty,
    professors,
    selectedProfessorId,
    handleProfessorChange
  };
};
