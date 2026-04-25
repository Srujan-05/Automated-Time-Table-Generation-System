import { useState } from "react";
import { useForm } from "react-hook-form";
import { mockData } from "@/lib/mockData";
import { toast } from "sonner";

export const useConstraints = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { constraintOptions } = mockData;

  const form = useForm({
    defaultValues: {
      maxConsecutiveHours: "2",
      preferredRoomType: "lecture"
    }
  });

  const onSubmit = (values: any) => {
    setIsSubmitting(true);
    setTimeout(() => {
      console.log("Constraints updated:", values);
      toast.success("Constraints updated successfully");
      setIsSubmitting(false);
    }, 1000);
  };

  return {
    form,
    onSubmit: form.handleSubmit(onSubmit),
    isSubmitting,
    options: constraintOptions
  };
};
