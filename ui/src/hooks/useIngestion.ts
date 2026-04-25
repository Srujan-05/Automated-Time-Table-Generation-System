import { useState } from "react";
import { toast } from "sonner";
import type { FileUpload } from "@/lib/types";
import { mockData } from "@/lib/mockData";

export const useIngestion = () => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [files, setFiles] = useState<FileUpload[]>([]);
  const [isImporting, setIsImporting] = useState(false);
  const { ingestionTypes } = mockData;

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    
    Array.from(fileList).forEach(file => {
      const newFile: FileUpload = { name: file.name, status: "uploading" };
      setFiles(prev => [...prev, newFile]);
      
      setTimeout(() => {
        setFiles(prev => prev.map(f => 
          f.name === file.name ? { ...f, status: "completed" } : f
        ));
        toast.success(`${file.name} uploaded`);
      }, 1500);
    });
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    processFiles(e.dataTransfer.files as any);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    processFiles(e.target.files as any);
  };

  const handleImport = () => {
    if (files.length === 0) {
        toast.error("Please upload files first");
        return;
    }
    setIsImporting(true);
    setTimeout(() => {
        setIsImporting(false);
        toast.success("Data imported to database");
        setFiles([]);
    }, 2000);
  };

  return {
    dragActive,
    files,
    handleDrag,
    handleDrop,
    handleFileChange,
    handleImport,
    isImporting,
    ingestionTypes
  };
};
