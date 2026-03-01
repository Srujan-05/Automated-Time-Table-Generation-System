
import { mockData } from "../lib/mockData";
import { Envelope, IdentificationBadge, Gear, ShieldCheck } from "@phosphor-icons/react";
import type { User as UserType } from "../lib/types";

const Profile = () => {
    const user: UserType = mockData.users.admin;

  return (
    <div className="max-w-2xl mx-auto space-y-8 pt-10">
      <div className="relative">
         <div className="h-32 bg-gradient-to-r from-red-900 to-black rounded-t-3xl border-x border-t border-zinc-800" />
         <div className="absolute -bottom-12 left-8 p-1 bg-black rounded-full z-10">
            <img src={user.avatar} alt="Avatar" className="w-24 h-24 rounded-full border-4 border-black" />
         </div>
      </div>
      
      <div className="pt-16 px-8 pb-8 bg-zinc-900/40 border border-zinc-800 rounded-b-3xl -mt-8 backdrop-blur-sm">
         <div className="flex justify-between items-start">
            <div>
                <h1 className="text-3xl font-bold text-white">{user.name}</h1>
                <p className="text-zinc-400 flex items-center gap-2 mt-1">
                    <ShieldCheck className="text-red-500" weight="fill" /> 
                    System Administrator
                </p>
            </div>
            <button className="px-4 py-2 rounded-lg bg-zinc-800 text-zinc-300 hover:bg-zinc-700 transition-colors text-sm font-medium">Edit Profile</button>
         </div>

         <div className="mt-8 space-y-4">
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 flex items-center gap-4">
                <div className="p-2 bg-zinc-900 rounded-lg text-zinc-400"><Envelope size={20} /></div>
                <div>
                    <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider">Email</p>
                    <p className="text-zinc-200">{user.email}</p>
                </div>
            </div>
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 flex items-center gap-4">
                <div className="p-2 bg-zinc-900 rounded-lg text-zinc-400"><IdentificationBadge size={20} /></div>
                <div>
                    <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider">Employee ID</p>
                    <p className="text-zinc-200">ADM-2026-X99</p>
                </div>
            </div>
         </div>

         <div className="mt-8 border-t border-zinc-800 pt-8">
            <h3 className="text-white font-bold mb-4 flex items-center gap-2"><Gear /> Settings</h3>
            <div className="space-y-2">
                {["Email Notifications", "Two-Factor Auth", "Dark Mode (Locked)"].map((setting) => (
                    <div key={setting} className="flex items-center justify-between p-3 rounded-lg hover:bg-zinc-800/50 transition-colors cursor-pointer">
                        <span className="text-zinc-300">{setting}</span>
                        <div className="w-10 h-6 bg-zinc-800 rounded-full relative">
                            <div className="absolute right-1 top-1 w-4 h-4 bg-green-500 rounded-full shadow-[0_0_10px_#22c55e]" />
                        </div>
                    </div>
                ))}
            </div>
         </div>
      </div>
    </div>
  );
};

export default Profile;
