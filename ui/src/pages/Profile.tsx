import { EnvelopeIcon, ShieldCheckIcon } from "@phosphor-icons/react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
        switch(role?.toLowerCase()) {
            case "admin": return "System Administrator";
            case "faculty": return "Faculty Member";
            case "student": return "Student";
            default: return role || "User";
        }
    };

  return (
    <div className="max-w-2xl mx-auto space-y-8 pt-10 pb-12">
      <Card className="border-none bg-transparent shadow-none overflow-visible py-0 rounded-3xl">
        <CardHeader className="p-0 relative h-40 bg-gradient-to-r from-primary/80 to-primary rounded-t-3xl overflow-hidden">
          <div className="absolute inset-0 bg-grid-white/10" />
          <div className="absolute bottom-5 left-8 p-1.5 bg-background rounded-full shadow-xl">
            <img 
              src={`https://ui-avatars.com/api/?name=${user.name}&background=ef4444&color=fff`} 
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
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;
