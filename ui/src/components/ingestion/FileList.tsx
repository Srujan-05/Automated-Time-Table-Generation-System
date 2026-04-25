import React from "react";
import { motion } from "framer-motion";
import { FileCsvIcon, CheckCircleIcon, CircleNotchIcon } from "@phosphor-icons/react";
import { type FileUpload } from "@/lib/types";

interface FileListProps {
  files: FileUpload[];
}

export const FileList: React.FC<FileListProps> = ({ files }) => {
  if (files.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wider px-1">Uploaded Files</h3>
      {files.map((file, i) => (
        <motion.div 
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between p-4 bg-card/50 border border-border rounded-xl"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <FileCsvIcon className="w-5 h-5 text-primary" />
            </div>
            <span className="text-foreground font-mono text-sm font-medium">{file.name}</span>
          </div>
          {file.status === "uploading" ? (
            <div className="flex items-center gap-2 text-muted-foreground text-xs uppercase font-bold tracking-wider">
              <CircleNotchIcon className="w-4 h-4 animate-spin" />
              Uploading...
            </div>
          ) : (
            <div className="flex items-center gap-2 text-green-500 text-xs uppercase font-bold tracking-wider">
              <CheckCircleIcon weight="fill" className="w-4 h-4" />
              Completed
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
};
