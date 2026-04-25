import { EnvelopeIcon, IdentificationBadgeIcon, GearIcon, ShieldCheckIcon } from "@phosphor-icons/react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { useProfile } from "@/hooks/useProfile";
import { Skeleton } from "@/components/ui/skeleton";

const Profile = () => {
    const { isLoading, user } = useProfile();

    if (isLoading) {
        return (
            <div className="max-w-2xl mx-auto space-y-8 pt-10 pb-12">
                <Skeleton className="h-40 rounded-3xl" />
                <Card className="p-8 space-y-6">
                    <Skeleton className="h-12 w-64" />
                    <Skeleton className="h-20 w-full" />
                    <Skeleton className="h-20 w-full" />
                </Card>
            </div>
        );
    }

    const getRoleBadge = (role: string) => {
        switch(role) {
            case "admin": return "System Administrator";
            case "faculty": return "Faculty Member";
            case "student": return "Student";
            default: return "User";
        }
    };

    const getIdentifierLabel = (role: string) => {
        switch(role) {
            case "admin": return "Employee ID";
            case "faculty": return "Faculty ID";
            case "student": return "Roll Number";
            default: return "ID";
        }
    };

    const getIdentifierValue = (user: any) => {
        if (user.role === "admin") return `ADM-2026-${user.id.toString().padStart(3, "0")}`;
        if (user.role === "faculty") return `FAC-2026-${user.id.toString().padStart(3, "0")}`;
        return `STU-2026-${user.id.toString().padStart(3, "0")}`;
    };

  return (
    <div className="max-w-2xl mx-auto space-y-8 pt-10 pb-12">
      <Card className="border-none bg-transparent shadow-none overflow-visible py-0 rounded-3xl">
        <CardHeader className="p-0 relative h-40 bg-gradient-to-r from-primary/80 to-primary rounded-t-3xl overflow-hidden">
          <div className="absolute inset-0 bg-grid-white/10" />
          <div className="absolute bottom-5 left-8 p-1.5 bg-background rounded-full shadow-xl">
            <img 
              src={user.avatar} 
              alt={user.name} 
              className="w-24 h-24 rounded-full border-2 border-border object-cover" 
            />
          </div>
        </CardHeader>
        
        <CardContent className="pt-8 px-8 pb-8 bg-card/40 border border-border border-t-0 rounded-b-3xl backdrop-blur-sm">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground">{user.name}</h1>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 gap-1.5 py-4 px-3">
                  <ShieldCheckIcon weight="fill" size={14} /> 
                  {getRoleBadge(user.role)}
                </Badge>
              </div>
            </div>
            <Button variant="outline" className="h-12 px-6 rounded-xl font-medium">
              Edit Profile
            </Button>
          </div>

          <div className="mt-10 space-y-4">
            <div className="p-4 rounded-2xl bg-muted/30 border border-border/50 flex items-center gap-4 group hover:bg-muted/50 transition-colors">
              <div className="p-2.5 bg-card rounded-xl text-muted-foreground group-hover:text-primary transition-colors border border-border/50">
                <EnvelopeIcon size={22} />
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Email Address</p>
                <p className="text-foreground font-medium">{user.email}</p>
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-muted/30 border border-border/50 flex items-center gap-4 group hover:bg-muted/50 transition-colors">
              <div className="p-2.5 bg-card rounded-xl text-muted-foreground group-hover:text-primary transition-colors border border-border/50">
                <IdentificationBadgeIcon size={22} />
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">{getIdentifierLabel(user.role)}</p>
                <p className="text-foreground font-medium font-mono">{getIdentifierValue(user)}</p>
              </div>
            </div>
            
            {user.dept && (
              <div className="p-4 rounded-2xl bg-muted/30 border border-border/50 flex items-center gap-4 group hover:bg-muted/50 transition-colors">
                <div className="p-2.5 bg-card rounded-xl text-muted-foreground group-hover:text-primary transition-colors border border-border/50">
                  <IdentificationBadgeIcon size={22} />
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Department</p>
                  <p className="text-foreground font-medium">{user.dept}</p>
                </div>
              </div>
            )}

            {user.batch && (
              <div className="p-4 rounded-2xl bg-muted/30 border border-border/50 flex items-center gap-4 group hover:bg-muted/50 transition-colors">
                <div className="p-2.5 bg-card rounded-xl text-muted-foreground group-hover:text-primary transition-colors border border-border/50">
                  <IdentificationBadgeIcon size={22} />
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Batch</p>
                  <p className="text-foreground font-medium">{user.batch}</p>
                </div>
              </div>
            )}
          </div>

          <Separator className="my-10 opacity-50" />

          <div className="space-y-6">
            <div className="flex items-center gap-2 font-bold text-foreground">
              <GearIcon size={20} />
              <h3>System Settings</h3>
            </div>
            
            <div className="space-y-2">
              {[
                { label: "Email Notifications", active: true },
                { label: "Two-Factor Authentication", active: false },
                { label: "System Maintenance Alerts", active: true }
              ].map((setting) => (
                <div key={setting.label} className="flex items-center justify-between p-4 rounded-xl hover:bg-muted/30 transition-colors cursor-pointer group">
                  <span className="text-muted-foreground font-medium group-hover:text-foreground">{setting.label}</span>
                  <div className={cn(
                    "w-10 h-6 rounded-full relative transition-colors duration-300",
                    setting.active ? "bg-primary/20" : "bg-muted"
                  )}>
                    <div className={cn(
                      "absolute top-1 w-4 h-4 rounded-full transition-all duration-300 shadow-sm",
                      setting.active 
                        ? "right-1 bg-primary shadow-primary/50" 
                        : "left-1 bg-muted-foreground"
                    )} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;
