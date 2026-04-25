import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/common/Spinner";

interface ConstraintSettingsProps {
  form: any;
  onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void>;
  isSubmitting: boolean;
  options: {
    maxConsecutiveHours: { label: string, value: string }[];
    preferredRoomTypes: { label: string, value: string }[];
  };
}

export const ConstraintSettings: React.FC<ConstraintSettingsProps> = ({
  form,
  onSubmit,
  isSubmitting,
  options
}) => {
  return (
    <Card className="bg-card/40 border-border p-6 rounded-2xl">
      <CardHeader className="p-0 mb-6">
        <CardTitle className="text-xl font-bold text-foreground">Constraint Settings</CardTitle>
      </CardHeader>
      <CardContent className="p-0 space-y-6">
        <form onSubmit={onSubmit} className="space-y-6">
            <div className="flex items-center justify-between gap-4">
            <Label className="text-muted-foreground text-sm font-medium">Max consecutive hours</Label>
            <Select 
                onValueChange={(val) => form.setValue("maxConsecutiveHours", val)} 
                defaultValue={form.getValues("maxConsecutiveHours")}
            >
                <SelectTrigger className="w-[140px] bg-card rounded-xl">
                <SelectValue placeholder="Select hours" />
                </SelectTrigger>
                <SelectContent>
                {options.maxConsecutiveHours.map(opt => (
                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                ))}
                </SelectContent>
            </Select>
            </div>

            <div className="flex items-center justify-between gap-4">
            <Label className="text-muted-foreground text-sm font-medium">Preferred Room Type</Label>
            <Select 
                onValueChange={(val) => form.setValue("preferredRoomType", val)} 
                defaultValue={form.getValues("preferredRoomType")}
            >
                <SelectTrigger className="w-[140px] bg-card rounded-xl">
                <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                {options.preferredRoomTypes.map(opt => (
                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                ))}
                </SelectContent>
            </Select>
            </div>

            <Button type="submit" disabled={isSubmitting} className="w-full rounded-xl">
                {isSubmitting && <Spinner className="mr-2" />}
                Save Constraints
            </Button>
        </form>
      </CardContent>
    </Card>
  );
};
