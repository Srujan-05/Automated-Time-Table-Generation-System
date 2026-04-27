import React from "react";
import { CheckCircleIcon, UsersIcon } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { usePreferences } from "@/hooks/usePreferences";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/common/Spinner";

const Preferences: React.FC = () => {
  const { 
    isLoading, 
    isSubmitting, 
    selectedShift,
    setSelectedShift,
    submitPreferences,
    isAdmin,
    professors,
    selectedProfessorId,
    handleProfessorChange
  } = usePreferences();

  if (isLoading) {
    return (
        <div className="space-y-8 max-w-2xl mx-auto pb-12">
            <div className="flex justify-between items-center">
                <Skeleton className="h-12 w-64" />
                <Skeleton className="h-12 w-48" />
            </div>
            <Skeleton className="h-64 rounded-3xl" />
        </div>
    );
  }

  const selectedProfName = professors.find(p => p.id.toString() === selectedProfessorId)?.name;

  return (
    <div className="space-y-8 max-w-2xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight mb-2">
            {isAdmin ? "Manage Preferences" : "Faculty Preferences"}
          </h1>
          <p className="text-muted-foreground">
            {isAdmin ? "Oversee and update teaching windows for faculty members." : "Select your primary teaching shift."}
          </p>
        </div>
        <Button 
          onClick={submitPreferences}
          disabled={isSubmitting || (isAdmin && !selectedProfessorId)}
          className="h-12 px-8 rounded-xl font-bold shadow-lg shadow-primary/20 flex items-center gap-2 transition-all active:scale-95"
        >
          {isSubmitting ? <Spinner /> : <CheckCircleIcon weight="fill" size={20} />}
          {isAdmin ? "Update Faculty" : "Save Changes"}
        </Button>
      </div>

      <div className="space-y-6">
        {isAdmin && (
            <Card className="bg-primary/5 border-primary/20 rounded-3xl backdrop-blur-sm">
                <CardHeader>
                    <div className="flex items-center gap-2 text-primary">
                        <UsersIcon weight="bold" size={20} />
                        <CardTitle className="text-lg">Professor Selection</CardTitle>
                    </div>
                    <CardDescription className="text-primary/70">Select a faculty member to manage their teaching window.</CardDescription>
                </CardHeader>
                <CardContent>
                    <Select value={selectedProfessorId} onValueChange={handleProfessorChange}>
                        <SelectTrigger className="w-full h-12 bg-background/50 rounded-xl border-primary/20">
                            <SelectValue placeholder="Select a professor" />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl">
                            {professors.map(prof => (
                                <SelectItem key={prof.id} value={prof.id.toString()}>
                                    {prof.name} ({prof.email})
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </CardContent>
            </Card>
        )}

        <Card className="bg-card/40 border-border rounded-3xl backdrop-blur-sm overflow-hidden pt-0">
            <CardHeader className="bg-muted/30 pt-6 pb-8">
                <CardTitle className="text-xl">Teaching Window</CardTitle>
                <CardDescription>
                    {isAdmin 
                        ? (selectedProfName ? `Adjust the preferred teaching block for ${selectedProfName}.` : "Select a professor above to see their preferences.") 
                        : "Select the block of time you are most available for classes."}
                </CardDescription>
            </CardHeader>
            <CardContent className="p-8 space-y-6">
                <div className="space-y-3">
                    <Label className="text-sm font-bold text-muted-foreground uppercase tracking-wider">Shift Preference</Label>
                    <Select 
                        value={selectedShift.toString()} 
                        onValueChange={(val) => setSelectedShift(Number(val))}
                        disabled={isAdmin && !selectedProfessorId}
                    >
                        <SelectTrigger className="w-full h-14 bg-background/50 rounded-2xl border-border/50 text-lg">
                            <SelectValue placeholder="Select shift" />
                        </SelectTrigger>
                        <SelectContent className="rounded-2xl border-border/50">
                            <SelectItem value="1" className="py-3 rounded-xl">Morning Shift (09:00 - 13:00)</SelectItem>
                            <SelectItem value="2" className="py-3 rounded-xl">Afternoon Shift (13:00 - 17:00)</SelectItem>
                            <SelectItem value="3" className="py-3 rounded-xl">Flexible Shift (No Preference)</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="p-4 rounded-2xl bg-primary/5 border border-primary/20">
                    <p className="text-sm text-muted-foreground leading-relaxed">
                        <span className="font-bold text-primary mr-1">Constraint Note:</span> 
                        The Genetic Algorithm prioritizes these bins. If multiple professors select the same shift and space is tight, 
                        the algorithm will distribute them based on room availability.
                    </p>
                </div>
            </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Preferences;
