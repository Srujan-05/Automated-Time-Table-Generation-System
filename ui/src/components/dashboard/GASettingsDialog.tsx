import React from "react";
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogDescription,
    DialogFooter
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface GASettingsDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (config: any) => void;
    isGenerating: boolean;
}

export const GASettingsDialog: React.FC<GASettingsDialogProps> = ({ 
    isOpen, 
    onClose, 
    onConfirm,
    isGenerating
}) => {
    const [config, setConfig] = React.useState({
        slots: 10,
        population_size: 50,
        max_generations: 100,
        min_generations: 10
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setConfig(prev => ({ ...prev, [name]: parseInt(value) || 0 }));
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[425px] rounded-3xl bg-card">
                <DialogHeader>
                    <DialogTitle>GA Engine Configuration</DialogTitle>
                    <DialogDescription>
                        Tune the stochastic solver parameters before generation.
                    </DialogDescription>
                </DialogHeader>
                
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="slots" className="text-right">Slots</Label>
                        <Input id="slots" name="slots" type="number" value={config.slots} onChange={handleChange} className="col-span-3" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="pop" className="text-right">Candidates</Label>
                        <Input id="pop" name="population_size" type="number" value={config.population_size} onChange={handleChange} className="col-span-3" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="max_gen" className="text-right">Max Iter</Label>
                        <Input id="max_gen" name="max_generations" type="number" value={config.max_generations} onChange={handleChange} className="col-span-3" />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <Label htmlFor="min_gen" className="text-right">Min Iter</Label>
                        <Input id="min_gen" name="min_generations" type="number" value={config.min_generations} onChange={handleChange} className="col-span-3" />
                    </div>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={onClose} disabled={isGenerating}>Cancel</Button>
                    <Button onClick={() => onConfirm(config)} disabled={isGenerating}>
                        {isGenerating ? "Running..." : "Start Solver"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};
