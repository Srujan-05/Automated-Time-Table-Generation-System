import React from "react";
import { motion } from "framer-motion";
import { UploadSimpleIcon } from "@phosphor-icons/react";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  dragActive: boolean;
  onDrag: (e: React.DragEvent<HTMLDivElement>) => void;
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({ 
  dragActive, 
  onDrag, 
  onDrop, 
  onFileChange 
}) => {
  return (
    <motion.div
      onDragEnter={onDrag}
      onDragLeave={onDrag}
      onDragOver={onDrag}
      onDrop={onDrop}
      animate={{ 
        scale: dragActive ? 1.01 : 1, 
        borderColor: dragActive ? "var(--color-primary)" : "var(--color-border)" 
      }}
      className={cn(
        "relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300",
        dragActive ? "bg-primary/5 border-primary" : "bg-card/20 border-border"
      )}
    >
      <div className="pointer-events-none flex flex-col items-center gap-4">
        <div className="p-4 rounded-full bg-secondary text-muted-foreground mb-2">
          <UploadSimpleIcon className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-foreground">Drag & drop your CSV files here</h3>
        <p className="text-muted-foreground">or click to browse from your computer</p>
      </div>
      <input 
        type="file" 
        multiple
        accept=".csv"
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
        onChange={onFileChange}
      />
    </motion.div>
  );
};

